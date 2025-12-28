"""AI Engine bridge for YOLOv8

Loads YOLO model once (via init_model) and exposes detect_frame.
If ultralytics is not installed, returns mock detections.
"""
from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional
from threading import Lock

_MODEL = None
_MODEL_LOCK = Lock()


def _load_yolo() -> Optional[Any]:
    """Attempt to load ultralytics YOLO model."""
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
                    pass
            except Exception:
                _MODEL = None
    return _MODEL


def init_model() -> Optional[Any]:
    """Public initializer to load model at app startup."""
    return _load_yolo()


def _boxes_from_result(r) -> List[Dict[str, Any]]:
    objs: List[Dict[str, Any]] = []
    boxes = getattr(r, "boxes", None)
    if boxes is None:
        return objs
    names = getattr(r, "names", None)
    for b in boxes:
        try:
            xyxy = getattr(b, "xyxy", None)
            conf = float(getattr(b, "conf", 0.0))
            cls = int(getattr(b, "cls", -1))
            if xyxy is not None:
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
    """Run detection on raw image bytes."""
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    model = _load_yolo()
    if model is None:
        return {
            "model": "mock",
            "timestamp": ts,
            "objects": [{"class": "person", "confidence": 0.6, "bbox": [10, 10, 100, 200], "box": [10, 10, 100, 200]}],
            "raw": None,
        }

    try:
        results = model.predict(source=frame_bytes, conf=conf_thresh, imgsz=640)
        all_objs: List[Dict[str, Any]] = []
        for r in results:
            objs = _boxes_from_result(r)
            all_objs.extend(objs)
        return {
            "model": getattr(model, "model", "yolov8"),
            "timestamp": ts,
            "objects": all_objs,
            "raw": None,
        }
    except Exception as e:
        return {"model": "yolov8_error", "timestamp": ts, "objects": [], "raw": {"error": str(e)}}
