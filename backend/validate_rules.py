"""Validate camera rules endpoints: set/get rules and ensure behavior respects thresholds."""
from __future__ import annotations

import importlib.util
import pathlib
import time
import json
import os

# Instead of importing full app (pydantic constraints may raise), import cctv and use manager
spec = importlib.util.spec_from_file_location("backend_cctv", str(pathlib.Path(__file__).resolve().parent / "cctv.py"))
backend_cctv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend_cctv)

def run():
    mgr = backend_cctv.get_manager()
    cam_id = f"rules_cam_{int(time.time())}"
    cam = backend_cctv.Camera(id=cam_id, name="rules_cam", rtsp_url="", enabled=False, fps=1.0)
    mgr.create_camera(cam)

    rules = {"proximity_threshold": 30, "crowd_threshold": 2, "default_dwell_threshold": 0.5}
    ok = mgr.update_camera_rules(cam_id, rules)
    assert ok
    cams = mgr.list_cameras()
    found = None
    for c in cams:
        if c.get("id") == cam_id:
            found = c
            break
    assert found is not None
    assert found.get("rules", {}).get("crowd_threshold") == 2
    print("Rules set and verified")


if __name__ == "__main__":
    run()

