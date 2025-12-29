"""
HAZM TUWAIQ - Stream Manager
Manage multiple camera streams centrally
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import threading
from collections import defaultdict

from .rtsp_handler import RTSPHandler


class StreamManager:
    """
    مدير البث المركزي لجميع الكاميرات
    Central manager for all camera streams
    """
    
    def __init__(self):
        """Initialize stream manager"""
        self.logger = logging.getLogger(__name__)
        
        # Active streams
        self.streams: Dict[str, RTSPHandler] = {}
        
        # Camera configurations
        self.camera_configs: Dict[str, Dict] = {}
        
        # Statistics aggregation
        self.global_stats = {
            'total_cameras': 0,
            'active_cameras': 0,
            'total_frames_captured': 0,
            'start_time': datetime.now().isoformat()
        }
        
        # Lock for thread safety
        self.lock = threading.Lock()
    
    def add_camera(
        self, 
        camera_id: str,
        rtsp_url: str,
        name: str = "",
        location: str = "",
        auto_start: bool = True
    ) -> bool:
        """
        Add camera to manager
        
        Args:
            camera_id: Unique camera ID
            rtsp_url: RTSP stream URL
            name: Camera friendly name
            location: Physical location
            auto_start: Whether to start streaming immediately
            
        Returns:
            Success status
        """
        with self.lock:
            if camera_id in self.streams:
                self.logger.warning(f"Camera {camera_id} already exists")
                return False
            
            try:
                # Create RTSP handler
                handler = RTSPHandler(
                    camera_id=camera_id,
                    rtsp_url=rtsp_url
                )
                
                # Store configuration
                self.camera_configs[camera_id] = {
                    'camera_id': camera_id,
                    'name': name or camera_id,
                    'location': location,
                    'rtsp_url': rtsp_url,
                    'added_time': datetime.now().isoformat()
                }
                
                # Add to streams
                self.streams[camera_id] = handler
                self.global_stats['total_cameras'] += 1
                
                # Auto-start if requested
                if auto_start:
                    handler.start()
                    self.global_stats['active_cameras'] += 1
                
                self.logger.info(f"✅ Added camera {camera_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to add camera {camera_id}: {e}")
                return False
    
    def remove_camera(self, camera_id: str) -> bool:
        """Remove camera from manager"""
        with self.lock:
            if camera_id not in self.streams:
                self.logger.warning(f"Camera {camera_id} not found")
                return False
            
            try:
                # Stop stream
                self.streams[camera_id].stop()
                
                # Remove
                del self.streams[camera_id]
                del self.camera_configs[camera_id]
                
                self.global_stats['total_cameras'] -= 1
                self.global_stats['active_cameras'] -= 1
                
                self.logger.info(f"Removed camera {camera_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to remove camera {camera_id}: {e}")
                return False
    
    def start_camera(self, camera_id: str) -> bool:
        """Start streaming from camera"""
        with self.lock:
            if camera_id not in self.streams:
                self.logger.error(f"Camera {camera_id} not found")
                return False
            
            try:
                self.streams[camera_id].start()
                self.global_stats['active_cameras'] += 1
                self.logger.info(f"Started camera {camera_id}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to start camera {camera_id}: {e}")
                return False
    
    def stop_camera(self, camera_id: str) -> bool:
        """Stop streaming from camera"""
        with self.lock:
            if camera_id not in self.streams:
                self.logger.error(f"Camera {camera_id} not found")
                return False
            
            try:
                self.streams[camera_id].stop()
                self.global_stats['active_cameras'] -= 1
                self.logger.info(f"Stopped camera {camera_id}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to stop camera {camera_id}: {e}")
                return False
    
    def get_frame(self, camera_id: str) -> Optional[Any]:
        """Get latest frame from camera"""
        if camera_id not in self.streams:
            return None
        
        return self.streams[camera_id].get_latest_frame()
    
    def get_camera_info(self, camera_id: str) -> Optional[Dict]:
        """Get camera information and stats"""
        if camera_id not in self.streams:
            return None
        
        config = self.camera_configs.get(camera_id, {})
        stats = self.streams[camera_id].get_stats()
        
        return {
            **config,
            'stats': stats
        }
    
    def list_cameras(self) -> List[Dict]:
        """List all cameras"""
        cameras = []
        
        for camera_id in self.streams.keys():
            info = self.get_camera_info(camera_id)
            if info:
                cameras.append(info)
        
        return cameras
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics"""
        
        # Update global stats
        total_frames = sum(
            stream.stats['frames_captured'] 
            for stream in self.streams.values()
        )
        
        self.global_stats['total_frames_captured'] = total_frames
        
        # Get per-camera stats
        camera_stats = {
            camera_id: stream.get_stats()
            for camera_id, stream in self.streams.items()
        }
        
        return {
            'global': self.global_stats,
            'cameras': camera_stats
        }
    
    def stop_all(self):
        """Stop all cameras"""
        with self.lock:
            for camera_id in list(self.streams.keys()):
                try:
                    self.streams[camera_id].stop()
                except:
                    pass
            
            self.global_stats['active_cameras'] = 0
            self.logger.info("Stopped all cameras")


# Singleton instance
_stream_manager: Optional[StreamManager] = None


def get_stream_manager() -> StreamManager:
    """Get singleton StreamManager instance"""
    global _stream_manager
    
    if _stream_manager is None:
        _stream_manager = StreamManager()
    
    return _stream_manager
