"""Validation script for behavior engine (Phase 3 MVP).

Creates synthetic detections and verifies alerts are persisted.
Run: python backend/validate_behavior.py
"""
from __future__ import annotations

import importlib.util
import pathlib
import time
import json

# load modules directly
spec = importlib.util.spec_from_file_location("backend_cctv", str(pathlib.Path(__file__).resolve().parent / "cctv.py"))
backend_cctv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend_cctv)

spec2 = importlib.util.spec_from_file_location("backend_behavior", str(pathlib.Path(__file__).resolve().parent / "behavior.py"))
backend_behavior = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(backend_behavior)


def run():
    cam_id = f"beh_test_{int(time.time())}"
    cam = backend_cctv.Camera(id=cam_id, name="beh_cam", rtsp_url="", enabled=False, fps=1.0, zones=[{"id":"zone1","poly":[[0,0],[0,1000],[1000,1000],[1000,0]],"dwell_threshold":1}])
    mgr = backend_cctv.get_manager()
    mgr.create_camera(cam)

    # synthetic detections: 3 persons clustered to trigger proximity/crowd
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    dets = [
        {"class": "person", "confidence": 0.9, "bbox": [10, 10, 60, 160], "track_id": 1},
        {"class": "person", "confidence": 0.8, "bbox": [30, 20, 80, 170], "track_id": 2},
        {"class": "person", "confidence": 0.85, "bbox": [200, 50, 250, 200], "track_id": 3},
    ]

    print("Processing synthetic detections...")
    backend_behavior.process_detections(cam_id, dets, ts=ts)

    print("Querying events...")
    events = backend_cctv.query_alerts(camera_id=cam_id, limit=10)
    print("Events count:", len(events))
    print(json.dumps(events, indent=2))

    print("Behavior validation complete")


if __name__ == "__main__":
    run()
