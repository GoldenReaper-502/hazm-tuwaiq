"""
HAZM TUWAIQ - RTSP Stream Handler
Handle RTSP camera streams with robust reconnection
"""

import cv2
import numpy as np
from typing import Optional, Dict, Any, Callable
import logging
import threading
import time
from datetime import datetime
from queue import Queue, Full


class RTSPHandler:
    """
    معالج بث RTSP للكاميرات
    RTSP stream handler with auto-reconnection
    """
    
    def __init__(
        self, 
        camera_id: str,
        rtsp_url: str,
        reconnect_interval: int = 5,
        frame_queue_size: int = 10
    ):
        """
        Initialize RTSP handler
        
        Args:
            camera_id: Unique camera identifier
            rtsp_url: RTSP stream URL (e.g., rtsp://admin:pass@192.168.1.100:554/stream)
            reconnect_interval: Seconds to wait before reconnecting
            frame_queue_size: Maximum frames to buffer
        """
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.reconnect_interval = reconnect_interval
        self.logger = logging.getLogger(f"RTSPHandler.{camera_id}")
        
        # Stream state
        self.capture: Optional[cv2.VideoCapture] = None
        self.is_connected = False
        self.is_running = False
        
        # Threading
        self.capture_thread: Optional[threading.Thread] = None
        self.frame_queue: Queue = Queue(maxsize=frame_queue_size)
        
        # Statistics
        self.stats = {
            'frames_captured': 0,
            'frames_dropped': 0,
            'reconnect_count': 0,
            'last_frame_time': None,
            'fps': 0,
            'connection_time': None
        }
        
        # Frame callback
        self.frame_callback: Optional[Callable] = None
    
    def connect(self) -> bool:
        """Connect to RTSP stream"""
        try:
            self.logger.info(f"Connecting to {self.rtsp_url}")
            
            # Open RTSP stream
            self.capture = cv2.VideoCapture(self.rtsp_url)
            
            # Configure capture
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 3)  # Reduce latency
            
            # Test connection
            ret, frame = self.capture.read()
            
            if ret and frame is not None:
                self.is_connected = True
                self.stats['connection_time'] = datetime.now().isoformat()
                self.logger.info(f"✅ Connected to camera {self.camera_id}")
                return True
            else:
                self.logger.error(f"❌ Failed to read frame from {self.camera_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            return False
    
    def start(self, frame_callback: Optional[Callable] = None):
        """
        Start capturing frames in background thread
        
        Args:
            frame_callback: Optional callback function(camera_id, frame, timestamp)
        """
        if self.is_running:
            self.logger.warning("Already running")
            return
        
        self.frame_callback = frame_callback
        
        # Connect if not connected
        if not self.is_connected:
            if not self.connect():
                self.logger.error("Failed to connect")
                return
        
        # Start capture thread
        self.is_running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        self.logger.info(f"Started capturing from {self.camera_id}")
    
    def stop(self):
        """Stop capturing frames"""
        self.is_running = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        
        if self.capture:
            self.capture.release()
            self.is_connected = False
        
        self.logger.info(f"Stopped capturing from {self.camera_id}")
    
    def _capture_loop(self):
        """Main capture loop running in background thread"""
        
        last_fps_check = time.time()
        fps_counter = 0
        
        while self.is_running:
            try:
                # Check connection
                if not self.is_connected or self.capture is None:
                    self.logger.warning("Lost connection, attempting reconnect...")
                    self.stats['reconnect_count'] += 1
                    
                    if self.connect():
                        continue
                    else:
                        time.sleep(self.reconnect_interval)
                        continue
                
                # Read frame
                ret, frame = self.capture.read()
                
                if not ret or frame is None:
                    self.logger.warning("Failed to read frame")
                    self.is_connected = False
                    continue
                
                # Update stats
                self.stats['frames_captured'] += 1
                self.stats['last_frame_time'] = datetime.now().isoformat()
                fps_counter += 1
                
                # Calculate FPS
                current_time = time.time()
                if current_time - last_fps_check >= 1.0:
                    self.stats['fps'] = fps_counter
                    fps_counter = 0
                    last_fps_check = current_time
                
                # Add to queue
                try:
                    self.frame_queue.put_nowait((frame, datetime.now()))
                except Full:
                    # Queue full, drop oldest frame
                    try:
                        self.frame_queue.get_nowait()
                        self.frame_queue.put_nowait((frame, datetime.now()))
                        self.stats['frames_dropped'] += 1
                    except:
                        pass
                
                # Call callback if provided
                if self.frame_callback:
                    try:
                        self.frame_callback(self.camera_id, frame, datetime.now())
                    except Exception as e:
                        self.logger.error(f"Callback error: {e}")
                
            except Exception as e:
                self.logger.error(f"Capture loop error: {e}")
                time.sleep(0.1)
    
    def get_latest_frame(self) -> Optional[np.ndarray]:
        """
        Get latest frame from queue
        
        Returns:
            Latest frame or None
        """
        try:
            # Get all frames and return latest
            frame = None
            while not self.frame_queue.empty():
                frame, _ = self.frame_queue.get_nowait()
            return frame
        except:
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get stream statistics"""
        return {
            'camera_id': self.camera_id,
            'is_connected': self.is_connected,
            'is_running': self.is_running,
            **self.stats
        }
    
    def __del__(self):
        """Cleanup on deletion"""
        self.stop()
