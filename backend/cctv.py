"""CCTV manager: camera registration, background workers, RTSP read,
store detections to SQLite. Built for stability: auto-reconnect,
per-camera worker threads, safe DB writes.
"""
from __future__ import annotations

import threading
import time
import json
import sqlite3
import os
from typing import Any, Dict, List, Optional

try:
    import cv2
    CV2_AVAILABLE = True
except Exception:
    CV2_AVAILABLE = False
import ai_engine
try:
    import behavior
    BEHAVIOR_AVAILABLE = True
except Exception:
    BEHAVIOR_AVAILABLE = False
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "cctv.db"
DB_LOCK = threading.Lock()

# Ensure DB exists and has required tables
def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS cameras (
                id TEXT PRIMARY KEY,
                name TEXT,
                rtsp_url TEXT,
                enabled INTEGER,
                fps REAL,
                zones TEXT,
                rules TEXT,
                created_at TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_id TEXT,
                ts TEXT,
                label TEXT,
                confidence REAL,
                bbox TEXT,
                raw TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_id TEXT,
                ts TEXT,
                event_type TEXT,
                severity TEXT,
                payload TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


class Camera:
    def __init__(self, id: str, name: str, rtsp_url: str, enabled: bool = False, fps: float = 2.0, zones: Optional[List[Dict]] = None, rules: Optional[Dict] = None):
        self.id = id
        self.name = name
        self.rtsp_url = rtsp_url
        self.enabled = enabled
        self.fps = fps or 2.0
        self.zones = zones or []
        self.rules = rules or {}
        self.created_at = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "rtsp_url": self.rtsp_url,
            "enabled": bool(self.enabled),
            "fps": float(self.fps),
            "zones": self.zones,
            "rules": self.rules,
            "created_at": self.created_at,
        }


class CameraWorker(threading.Thread):
    def __init__(self, camera: Camera, stop_event: threading.Event):
        super().__init__(daemon=True)
        self.camera = camera
        self.stop_event = stop_event
        self.capture = None
        self.last_frame_ts = None

    def run(self):
        # continuous loop with reconnect
        reconnect_delay = 2.0
        frame_interval = 1.0 / max(0.1, float(self.camera.fps))
        while not self.stop_event.is_set():
            try:
                if not CV2_AVAILABLE:
                    # if cv2 unavailable, sleep and still run inference on placeholder
                    time.sleep(frame_interval)
                    # produce a mock single detection by calling ai_engine with empty bytes
                    self._process_frame(b"")
                    continue

                # Open capture if needed
                if self.capture is None or not self.capture.isOpened():
                    self.capture = cv2.VideoCapture(self.camera.rtsp_url, cv2.CAP_FFMPEG)
                    # set small timeout / buffer
                    time.sleep(0.5)

                if not self.capture or not self.capture.isOpened():
                    time.sleep(reconnect_delay)
                    continue

                ret, frame = self.capture.read()
                if not ret or frame is None:
                    # connection issue — try reconnect
                    try:
                        self.capture.release()
                    except Exception:
                        pass
                    self.capture = None
                    time.sleep(reconnect_delay)
                    continue

                # encode frame to JPEG bytes
                try:
                    ok, buf = cv2.imencode('.jpg', frame)
                    if not ok:
                        time.sleep(frame_interval)
                        continue
                    frame_bytes = buf.tobytes()
                except Exception:
                    frame_bytes = b""

                # process detection
                self._process_frame(frame_bytes)

                # throttle by fps
                time.sleep(frame_interval)

            except Exception:
                # catch-all to avoid crashing the thread
                time.sleep(reconnect_delay)
                continue

        # cleanup
        try:
            if self.capture is not None:
                self.capture.release()
        except Exception:
            pass

    def _process_frame(self, frame_bytes: bytes) -> None:
        try:
            result = ai_engine.detect_frame(frame_bytes, conf_thresh=float(os.getenv("YOLO_CONF", "0.25")))
            objects = result.get("objects", []) if isinstance(result, dict) else []
            ts = result.get("timestamp") if isinstance(result, dict) else (datetime.utcnow().isoformat() + "Z")
            # persist detections
            for obj in objects:
                label = obj.get("class") or obj.get("label") or "unknown"
                conf = float(obj.get("confidence", 0.0))
                bbox = obj.get("bbox", obj.get("box", [0,0,0,0]))
                store_detection(self.camera.id, ts, label, conf, bbox, raw=result)
            # run behavior processing (best-effort)
            try:
                if BEHAVIOR_AVAILABLE:
                    # enrich with simple tracking if available
                    try:
                        from tracking import update as track_update
                        objs_tracked = track_update(self.camera.id, objects)
                    except Exception:
                        objs_tracked = objects
                    behavior.process_detections(self.camera.id, objs_tracked, ts=ts)
            except Exception:
                pass
        except Exception:
            # do not raise
            return


class CameraManager:
    def __init__(self):
        self.workers: Dict[str, Dict[str, Any]] = {}
        init_db()

    def create_camera(self, cam: Camera) -> None:
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("INSERT OR REPLACE INTO cameras (id, name, rtsp_url, enabled, fps, zones, rules, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (cam.id, cam.name, cam.rtsp_url, int(cam.enabled), float(cam.fps), json.dumps(cam.zones), json.dumps(cam.rules), cam.created_at))
            conn.commit()
            conn.close()

    def update_camera_rules(self, camera_id: str, rules: Dict[str, Any]) -> bool:
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT id FROM cameras WHERE id=?", (camera_id,))
            if not cur.fetchone():
                conn.close()
                return False
            cur.execute("UPDATE cameras SET rules=? WHERE id=?", (json.dumps(rules), camera_id))
            conn.commit()
            conn.close()
        return True

    def list_cameras(self) -> List[Dict[str, Any]]:
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT id, name, rtsp_url, enabled, fps, zones, rules, created_at FROM cameras")
            rows = cur.fetchall()
            conn.close()
        cams = []
        for r in rows:
            cams.append({
                "id": r[0],
                "name": r[1],
                "rtsp_url": r[2],
                "enabled": bool(r[3]),
                "fps": float(r[4]),
                "zones": json.loads(r[5]) if r[5] else [],
                "rules": json.loads(r[6]) if r[6] else {},
                "created_at": r[7],
            })
        return cams

    def update_camera_zones(self, camera_id: str, zones: List[Dict[str, Any]]) -> bool:
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT id FROM cameras WHERE id=?", (camera_id,))
            if not cur.fetchone():
                conn.close()
                return False
            cur.execute("UPDATE cameras SET zones=? WHERE id=?", (json.dumps(zones), camera_id))
            conn.commit()
            conn.close()
        return True

    def start_camera(self, camera_id: str) -> bool:
        # read camera row
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT id, name, rtsp_url, enabled, fps, zones, rules FROM cameras WHERE id=?", (camera_id,))
            row = cur.fetchone()
            conn.close()
        if not row:
            return False
        cam = Camera(id=row[0], name=row[1], rtsp_url=row[2], enabled=bool(row[3]), fps=float(row[4] or 2.0), zones=json.loads(row[5] or "[]"), rules=json.loads(row[6] or "{}"))
        if camera_id in self.workers and self.workers[camera_id]["running"]:
            return True
        stop_event = threading.Event()
        worker = CameraWorker(cam, stop_event)
        worker.start()
        self.workers[camera_id] = {"worker": worker, "stop_event": stop_event, "running": True}
        # mark enabled
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("UPDATE cameras SET enabled=1 WHERE id=?", (camera_id,))
            conn.commit()
            conn.close()
        return True

    def stop_camera(self, camera_id: str) -> bool:
        entry = self.workers.get(camera_id)
        if not entry:
            # still mark disabled in DB
            with DB_LOCK:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("UPDATE cameras SET enabled=0 WHERE id=?", (camera_id,))
                conn.commit()
                conn.close()
            return True
        entry["stop_event"].set()
        try:
            entry["worker"].join(timeout=3.0)
        except Exception:
            pass
        entry["running"] = False
        del self.workers[camera_id]
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("UPDATE cameras SET enabled=0 WHERE id=?", (camera_id,))
            conn.commit()
            conn.close()
        return True

    def status(self, camera_id: str) -> Dict[str, Any]:
        entry = self.workers.get(camera_id)
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT id, name, rtsp_url, enabled, fps, zones, rules, created_at FROM cameras WHERE id=?", (camera_id,))
            row = cur.fetchone()
            conn.close()
        if not row:
            return {"exists": False}
        return {
            "exists": True,
            "id": row[0],
            "name": row[1],
            "enabled": bool(row[3]),
            "running": bool(entry["running"]) if entry else False,
            "last_seen": getattr(entry["worker"], "last_frame_ts", None) if entry else None,
        }


# Persistence helpers
def store_detection(camera_id: str, ts: str, label: str, confidence: float, bbox: List[float], raw: Optional[Dict] = None) -> None:
    with DB_LOCK:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO detections (camera_id, ts, label, confidence, bbox, raw) VALUES (?, ?, ?, ?, ?, ?)",
                    (camera_id, ts, label, confidence, json.dumps(bbox), json.dumps(raw)))
        conn.commit()
        conn.close()


def store_alert(camera_id: str, ts: str, event_type: str, severity: str, payload: Optional[Dict] = None) -> None:
    with DB_LOCK:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO alerts (camera_id, ts, event_type, severity, payload) VALUES (?, ?, ?, ?, ?)",
                    (camera_id, ts, event_type, severity, json.dumps(payload)))
        conn.commit()
        conn.close()

    # dispatch webhook if camera has webhook_url in rules and sending enabled
    try:
        send_enabled = os.getenv("SEND_WEBHOOKS", "0").strip() == "1"
        if send_enabled:
            # fetch camera rules
            cam = None
            try:
                cam = query_cameras()
            except Exception:
                cam = None
            webhook_url = None
            if cam:
                for c in cam:
                    if c.get("id") == camera_id:
                        rules = c.get("rules", {}) or {}
                        webhook_url = rules.get("webhook_url")
                        break

            if webhook_url:
                def _dispatch():
                    try:
                        import requests
                        body = {
                            "camera_id": camera_id,
                            "ts": ts,
                            "event_type": event_type,
                            "severity": severity,
                            "payload": payload,
                        }
                        requests.post(webhook_url, json=body, timeout=5)
                    except Exception:
                        return

                t = threading.Thread(target=_dispatch, daemon=True)
                t.start()
    except Exception:
        pass


def query_detections(camera_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    with DB_LOCK:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        if camera_id:
            cur.execute("SELECT id, camera_id, ts, label, confidence, bbox, raw FROM detections WHERE camera_id=? ORDER BY id DESC LIMIT ?", (camera_id, limit))
        else:
            cur.execute("SELECT id, camera_id, ts, label, confidence, bbox, raw FROM detections ORDER BY id DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
    out = []
    for r in rows:
        out.append({
            "id": r[0],
            "camera_id": r[1],
            "ts": r[2],
            "label": r[3],
            "confidence": r[4],
            "bbox": json.loads(r[5]) if r[5] else None,
            "raw": json.loads(r[6]) if r[6] else None,
        })
    return out


def query_alerts(camera_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    with DB_LOCK:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        if camera_id:
            cur.execute("SELECT id, camera_id, ts, event_type, severity, payload FROM alerts WHERE camera_id=? ORDER BY id DESC LIMIT ?", (camera_id, limit))
        else:
            cur.execute("SELECT id, camera_id, ts, event_type, severity, payload FROM alerts ORDER BY id DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
    out = []
    for r in rows:
        out.append({
            "id": r[0],
            "camera_id": r[1],
            "ts": r[2],
            "event_type": r[3],
            "severity": r[4],
            "payload": json.loads(r[5]) if r[5] else None,
        })
    return out


# singleton manager
_MANAGER: Optional[CameraManager] = None


def get_manager() -> CameraManager:
    global _MANAGER
    if _MANAGER is None:
        _MANAGER = CameraManager()
    return _MANAGER


def query_cameras() -> List[Dict[str, Any]]:
    """Return list of cameras from DB (convenience wrapper)."""
    mgr = get_manager()
    return mgr.list_cameras()
