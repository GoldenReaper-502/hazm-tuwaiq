#!/usr/bin/env python
"""
YOLOv8 Model Pre-loader Script

This script downloads and caches the YOLOv8 model locally.
Useful for Docker builds or server initialization to avoid runtime downloads.

Usage:
    python download_yolo_model.py
    # or with custom model size:
    python download_yolo_model.py yolov8m  # medium model
"""
import sys
import os
from pathlib import Path

def download_model(model_name: str = "yolov8n"):
    """Download YOLOv8 model and cache it locally."""
    try:
        from ultralytics import YOLO
        
        print(f"🔄 Downloading YOLOv8 model: {model_name}...")
        model = YOLO(f"{model_name}.pt")
        
        print(f"✅ Model downloaded and cached successfully!")
        print(f"   Model: {model_name}")
        print(f"   Cache location: ~/.yolov8")
        print(f"   Next runs will use cached model (no re-download)")
        return True
    
    except ImportError:
        print("❌ ERROR: ultralytics not installed")
        print("   Install with: pip install ultralytics")
        return False
    
    except Exception as e:
        print(f"⚠️  Model download incomplete or failed: {e}")
        print("   Backend will attempt download at runtime")
        return False

if __name__ == "__main__":
    model_size = sys.argv[1] if len(sys.argv) > 1 else "yolov8n"
    success = download_model(model_size)
    sys.exit(0 if success else 1)
