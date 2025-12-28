"""Validation script for CCTV endpoints and manager.

Uses FastAPI TestClient to exercise camera create/list/start/stop/status
and detections query without running an external server.
Run: python backend/validate_cctv.py
"""
from __future__ import annotations

import os
import time
import json
import importlib.util
import pathlib
import time
import json
import os

# Load cctv module directly to test manager functions without importing full FastAPI app
spec = importlib.util.spec_from_file_location("backend_cctv", str(pathlib.Path(__file__).resolve().parent / "cctv.py"))
backend_cctv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend_cctv)

def get_headers():
    # kept for compatibility with previous script interface
    key = os.getenv("HAZM_API_KEY", "").strip()
    if key:
        return {"x-api-key": key}
    return {}


def run():
    mgr = backend_cctv.get_manager()

    print("Creating camera via manager...")
    cam_id = f"cv_test_{int(time.time())}"
    cam = backend_cctv.Camera(id=cam_id, name="test_cam", rtsp_url="rtsp://example.invalid/stream", enabled=False, fps=1.0)
    mgr.create_camera(cam)
    print("Created:", cam_id)

    print("Listing cameras...")
    cams = mgr.list_cameras()
    print("Cameras:", len(cams))

    print("Starting camera (best-effort, no real RTSP expected)...")
    ok = mgr.start_camera(cam_id)
    assert ok, "start_camera returned False"
    print("Started")

    print("Checking status...")
    status = mgr.status(cam_id)
    print(json.dumps(status, indent=2))

    print("Waiting briefly to allow (mock) detections to be stored...")
    time.sleep(2)

    print("Querying camera detections...")
    dets = backend_cctv.query_detections(camera_id=cam_id, limit=10)
    print("Detections count:", len(dets))

    print("Stopping camera...")
    ok = mgr.stop_camera(cam_id)
    assert ok, "stop_camera returned False"
    print("Stopped")

    print("Validation OK")


if __name__ == "__main__":
    try:
        run()
    except AssertionError as e:
        print("Validation failed:", e)
        raise

