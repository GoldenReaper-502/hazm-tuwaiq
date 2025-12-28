"""Simple IoU-based lightweight tracker used as a fallback when full trackers
are not available. Assigns persistent numeric `track_id` per camera for short
term identity across consecutive frames.
"""
from __future__ import annotations

from typing import List, Dict, Any
import threading
import math

# Per-camera tracker state
_TRACKERS: Dict[str, Dict[str, Any]] = {}
_LOCK = threading.Lock()


def _iou(boxA, boxB):
    # boxes are [x1,y1,x2,y2]
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interW = max(0.0, xB - xA)
    interH = max(0.0, yB - yA)
    interArea = interW * interH
    boxAArea = max(0.0, boxA[2] - boxA[0]) * max(0.0, boxA[3] - boxA[1])
    boxBArea = max(0.0, boxB[2] - boxB[0]) * max(0.0, boxB[3] - boxB[1])
    denom = boxAArea + boxBArea - interArea
    if denom <= 0:
        return 0.0
    return interArea / denom


def update(camera_id: str, detections: List[Dict[str, Any]], iou_threshold: float = 0.3) -> List[Dict[str, Any]]:
    """Assign `track_id` to each detection in-place and return list.

    detections: each item has `bbox` field
    """
    with _LOCK:
        st = _TRACKERS.setdefault(camera_id, {"next_id": 1, "last_boxes": {}})
        assigned = []
        new_last = {}
        for det in detections:
            bbox = det.get("bbox") or det.get("box") or [0, 0, 0, 0]
            best_id = None
            best_iou = 0.0
            for tid, prev in st["last_boxes"].items():
                prev_box = prev["bbox"]
                val = _iou(bbox, prev_box)
                if val > best_iou:
                    best_iou = val
                    best_id = tid

            if best_id is not None and best_iou >= iou_threshold:
                track_id = int(best_id)
            else:
                track_id = st["next_id"]
                st["next_id"] += 1

            det["track_id"] = track_id
            new_last[str(track_id)] = {"bbox": bbox}
            assigned.append(det)

        st["last_boxes"] = new_last
        return assigned
