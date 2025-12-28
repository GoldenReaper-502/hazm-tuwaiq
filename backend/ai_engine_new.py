"""AI Engine bridge for YOLOv8

Loads YOLO model once (via `init_model`) and exposes `detect_frame`.
If `ultralytics` is not installed the module returns mock detections so
the rest of the app continues working.
"""
from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional
from threading import Lock

_MODEL = None
_MODEL_LOCK = Lock()


def _load_yolo() -> Optional[Any]:
    """Attempt to load ultralytics YOLO model. Returns model or None."""
    global _MODEL
    try:
        from ultralytics import YOLO
    except Exception:
        return None

    model_name = os.getenv("YOLO_MODEL", "yolov8n.pt")
    device = os.getenv("TORCH_DEVICE", "cpu")

    with _MODEL_LOCK:
        if _MODEL is None:
            try:
                _MODEL = YOLO(model_name)
                try:
                    _MODEL.to(device)
                except Exception:
                    # device move best-effort
                    pass
            except Exception:
                _MODEL = None
    return _MODEL


def init_model() -> Optional[Any]:
    """Public initializer to load model at app startup (idempotent)."""
    return _load_yolo()


def _boxes_from_result(r) -> List[Dict[str, Any]]:
    objs: List[Dict[str, Any]] = []
    boxes = getattr(r, "boxes", None)
    if boxes is None:
        return objs

    # Try to get class names mapping if available
    names = getattr(r, "names", None)

    for b in boxes:
        try:
            xyxy = getattr(b, "xyxy", None)
            conf = float(getattr(b, "conf", 0.0))
            cls = int(getattr(b, "cls", -1))

            if xyxy is not None:
                # xyxy may be tensor-like
                try:
                    coords = [float(v) for v in xyxy.tolist()]
                except Exception:
                    coords = [float(v) for v in xyxy]
                x1, y1, x2, y2 = coords
            else:
                x1 = y1 = x2 = y2 = 0.0

            label = None
            if isinstance(names, dict):
                label = names.get(cls)
            if label is None:
                label = str(cls)

            objs.append({
                "class": label,
                "confidence": conf,
                "bbox": [x1, y1, x2, y2],
                "box": [x1, y1, x2, y2],
            })
        except Exception:
            continue

    return objs


def detect_frame(frame_bytes: bytes, conf_thresh: float = 0.25) -> Dict[str, Any]:
    """Run detection on raw image bytes.

    Returns a dict with keys: model, timestamp, objects, raw
    Each object contains: class, confidence, bbox (x1,y1,x2,y2) and box (same)
    """
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    model = _load_yolo()
    if model is None:
        # fallback mock
        return {
            "model": "mock",
            "timestamp": ts,
            "objects": [{"class": "person", "confidence": 0.6, "bbox": [10, 10, 100, 200], "box": [10, 10, 100, 200]}],
            "raw": None,
        }

    try:
        # ultralytics supports passing bytes directly as source
        results = model.predict(source=frame_bytes, conf=conf_thresh, imgsz=640)

        all_objs: List[Dict[str, Any]] = []
        raw = []
        for r in results:
            objs = _boxes_from_result(r)
            all_objs.extend(objs)
            raw.append(r)

        return {
            "model": getattr(model, "model", "yolov8"),
            "timestamp": ts,
            "objects": all_objs,
            "raw": None,
        }

    except Exception as e:
        return {"model": "yolov8_error", "timestamp": ts, "objects": [], "raw": {"error": str(e)}}


def detect_frame_enhanced(frame_bytes: bytes, conf_thresh: float = 0.25, tracked: bool = False, annotate: bool = False, camera_id: Optional[str] = None) -> Dict[str, Any]:
    """Enhanced detect: runs `detect_frame`, optional lightweight tracking and annotation.

    Returns same dict as `detect_frame` with optional keys in `raw`: `annotated_b64`.
    """
    base = detect_frame(frame_bytes, conf_thresh)
    objs = base.get("objects", [])

    # apply lightweight tracking if requested
    if tracked:
        try:
            from tracking import update as track_update
            objs = track_update(camera_id or "_local", objs)
        except Exception:
            pass

    annotated_b64 = None
    if annotate:
        try:
            try:
                import cv2
                CV2 = True
            except Exception:
                CV2 = False

            if CV2 and frame_bytes:
                import numpy as np
                import base64 as _b64
                arr = np.frombuffer(frame_bytes, dtype=np.uint8)
                img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                if img is not None:
                    for o in objs:
                        bbox = o.get("bbox") or o.get("box")
                        if not bbox:
                            continue
                        x1, y1, x2, y2 = [int(v) for v in bbox]
                        label = str(o.get("class", "obj"))
                        tid = o.get("track_id")
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        txt = f"{label} {o.get('confidence',0):.2f}"
                        if tid is not None:
                            txt += f" id:{tid}"
                        cv2.putText(img, txt, (x1, max(10, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    ok, buf = cv2.imencode('.jpg', img)
                    if ok:
                        annotated_b64 = _b64.b64encode(buf.tobytes()).decode()
        except Exception:
            annotated_b64 = None

    out = {
        "model": base.get("model", "yolov8"),
        "timestamp": base.get("timestamp"),
        "objects": objs,
        "raw": base.get("raw"),
    }
    if annotated_b64:
        out.setdefault("raw", {})
        out["raw"]["annotated_b64"] = annotated_b64
    return out
