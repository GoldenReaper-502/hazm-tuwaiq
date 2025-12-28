#!/usr/bin/env python3
"""Simple validation script to check YOLOv8 model is loadable and runs inference.

Usage: python validate_yolo.py
It will call `ai_engine.init_model()` and run detect on a tiny test image.
"""
from pathlib import Path
import sys
import base64
import requests
import os

from ai_engine import init_model, detect_frame


def download_sample(dest: Path) -> Path:
    url = os.getenv("YOLO_SAMPLE_IMAGE", "https://ultralytics.com/images/zidane.jpg")
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        dest.write_bytes(r.content)
        return dest
    except Exception as e:
        print(f"Failed to download sample image: {e}")
        return None


def main():
    print("Initializing YOLO model...")
    m = init_model()
    if m is None:
        print("YOLO model not available (ultralytics not installed) — aborting.")
        return 2

    print("Model loaded. Downloading sample image...")
    sample = Path(__file__).with_name("sample.jpg")
    if not sample.exists():
        p = download_sample(sample)
        if p is None:
            print("No sample available — exiting")
            return 3

    data = sample.read_bytes()
    print(f"Running detection on {sample} ({len(data)} bytes)...")
    res = detect_frame(data, conf_thresh=float(os.getenv("YOLO_CONF", "0.25")))
    print("Result model:", res.get("model"))
    print("Detected objects:")
    for o in res.get("objects", []):
        print(f" - {o.get('class') or o.get('label')} conf={o.get('confidence')} bbox={o.get('bbox') or o.get('box')}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
