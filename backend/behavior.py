"""Behavior intelligence engine (Phase 3 MVP).

Detects simple events from detections stream:
- zone_entry
- proximity
- dwell_time (basic)
- crowd_density

This module uses `cctv.store_alert` to persist events. It implements
lightweight polygon containment fallback (no shapely required).
"""
from __future__ import annotations

from typing import List, Dict, Any, Optional
import time
import math

try:
    from shapely.geometry import Point, Polygon
    SHAPELY = True
except Exception:
    SHAPELY = False

import cctv

# In-memory tracking for dwell-time: {camera_id: {track_id: {zone_id: enter_ts}}}
_DWELL: Dict[str, Dict[int, Dict[str, float]]] = {}


def _point_in_poly(x: float, y: float, poly: List[List[float]]) -> bool:
    # poly: [[x1,y1], [x2,y2], ...]
    if SHAPELY:
        return Polygon(poly).contains(Point(x, y))
    # ray casting fallback
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        intersect = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi)
        if intersect:
            inside = not inside
        j = i
    return inside


def _bbox_center(bbox: List[float]) -> (float, float):
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def process_detections(camera_id: str, detections: List[Dict[str, Any]], ts: Optional[str] = None) -> None:
    """Process detections and emit alerts via `cctv.store_alert`.

    Detections expected as list of dicts with keys: class, confidence, bbox, track_id (optional)
    """
    if ts is None:
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    try:
        cams = cctv.query_detections(camera_id=None, limit=1)  # ensure DB exists
    except Exception:
        pass

    # Load camera zones from DB
    cam_rows = cctv.query_cameras()
    cam_z = None
    for c in cam_rows:
        if c.get("id") == camera_id:
            cam_z = c
            break

    zones = cam_z.get("zones", []) if cam_z else []

    # Determine thresholds from camera rules (if present)
    proximity_threshold = 50
    crowd_threshold = 5
    default_dwell = 10
    if cam_z:
        cam_rules = cam_z.get("rules", {}) if isinstance(cam_z.get("rules", {}), dict) else {}
        proximity_threshold = float(cam_rules.get("proximity_threshold", proximity_threshold))
        crowd_threshold = int(cam_rules.get("crowd_threshold", crowd_threshold))
        default_dwell = float(cam_rules.get("default_dwell_threshold", default_dwell))

    # Crowd density
    persons = [d for d in detections if (d.get("class") or "").strip().lower() == "person"]
    if len(persons) >= crowd_threshold:
        payload = {"count": len(persons), "threshold": crowd_threshold}
        cctv.store_alert(camera_id, ts, "crowd_density", "medium", payload)

    # Proximity (pairwise)
    for i in range(len(persons)):
        for j in range(i + 1, len(persons)):
            b1 = persons[i].get("bbox", persons[i].get("box", [0, 0, 0, 0]))
            b2 = persons[j].get("bbox", persons[j].get("box", [0, 0, 0, 0]))
            x1, y1 = _bbox_center(b1)
            x2, y2 = _bbox_center(b2)
            dist = math.hypot(x2 - x1, y2 - y1)
            if dist < proximity_threshold:
                payload = {"distance_px": dist, "a": persons[i].get("track_id"), "b": persons[j].get("track_id")}
                cctv.store_alert(camera_id, ts, "proximity", "low", payload)

    # Zone entry & dwell
    for det in detections:
        bbox = det.get("bbox") or det.get("box") or [0, 0, 0, 0]
        cx, cy = _bbox_center(bbox)
        track_id = int(det.get("track_id") or -1)
        for z in zones:
            zid = z.get("id") or z.get("name") or "zone"
            poly = z.get("poly")
            if not poly:
                continue
            inside = _point_in_poly(cx, cy, poly)
            if inside:
                # check dwell
                cam_dw = _DWELL.setdefault(camera_id, {})
                track_dw = cam_dw.setdefault(track_id, {})
                if zid not in track_dw:
                    # enter event
                    payload = {"zone": zid, "track_id": track_id}
                    cctv.store_alert(camera_id, ts, "zone_entry", "medium", payload)
                    track_dw[zid] = time.time()
                else:
                    enter_ts = track_dw[zid]
                    dwell_threshold = float(z.get("dwell_threshold", default_dwell))
                    if time.time() - enter_ts > dwell_threshold:
                        payload = {"zone": zid, "track_id": track_id, "dwell_s": time.time() - enter_ts}
                        cctv.store_alert(camera_id, ts, "dwell_time", "high", payload)
