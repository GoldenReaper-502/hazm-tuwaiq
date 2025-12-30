"""
HAZM TUWAIQ - Pose Estimation Engine
Detect worker postures, falls, and ergonomic risks using YOLOv8-Pose
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
import math


def _get_cv2():
    """Lazy import cv2 to prevent startup crashes"""
    try:
        import cv2
        return cv2
    except ImportError as e:
        raise RuntimeError(f"OpenCV not available: {e}")


try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


class PoseEstimator:
    """
    تقدير وضعية الجسم لكشف السقوط والأوضاع الخطرة
    Pose estimation for fall detection and ergonomic analysis
    """
    
    # Keypoint indices for COCO pose format
    KEYPOINTS = {
        'nose': 0,
        'left_eye': 1, 'right_eye': 2,
        'left_ear': 3, 'right_ear': 4,
        'left_shoulder': 5, 'right_shoulder': 6,
        'left_elbow': 7, 'right_elbow': 8,
        'left_wrist': 9, 'right_wrist': 10,
        'left_hip': 11, 'right_hip': 12,
        'left_knee': 13, 'right_knee': 14,
        'left_ankle': 15, 'right_ankle': 16
    }
    
    def __init__(self, model_path: str = "yolov8n-pose.pt"):
        """
        Initialize pose estimator
        
        Args:
            model_path: Path to YOLOv8-Pose model
        """
        self.model_path = model_path
        self.model = None
        self.logger = logging.getLogger(__name__)
        
        # Load model
        self._load_model()
    
    def _load_model(self) -> bool:
        """Load YOLOv8-Pose model"""
        try:
            if not YOLO_AVAILABLE:
                self.logger.warning("YOLOv8 not available - using simulation mode")
                return False
            
            self.logger.info(f"Loading pose model: {self.model_path}")
            self.model = YOLO(self.model_path)
            self.logger.info("✅ Pose model loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load pose model: {e}")
            return False
    
    def estimate_pose(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Estimate human poses in image
        
        Args:
            image: Input image (BGR)
            
        Returns:
            Pose estimation results
        """
        if self.model is None:
            return self._simulate_pose(image)
        
        try:
            # Run pose estimation
            results = self.model(image, verbose=False)
            
            # Parse results
            poses = self._parse_poses(results[0])
            
            # Analyze poses for risks
            analysis = self._analyze_poses(poses)
            
            return {
                'poses': poses,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Pose estimation error: {e}")
            return self._simulate_pose(image)
    
    def _parse_poses(self, result) -> List[Dict[str, Any]]:
        """Parse pose estimation results"""
        poses = []
        
        if result.keypoints is None or len(result.keypoints) == 0:
            return poses
        
        # Extract keypoints
        keypoints_data = result.keypoints.xy.cpu().numpy()  # (N, 17, 2)
        confidences = result.keypoints.conf.cpu().numpy()   # (N, 17)
        
        for kpts, confs in zip(keypoints_data, confidences):
            # Build keypoint dictionary
            keypoints = {}
            for name, idx in self.KEYPOINTS.items():
                if idx < len(kpts):
                    keypoints[name] = {
                        'x': float(kpts[idx][0]),
                        'y': float(kpts[idx][1]),
                        'confidence': float(confs[idx])
                    }
            
            poses.append({
                'keypoints': keypoints,
                'avg_confidence': float(np.mean(confs))
            })
        
        return poses
    
    def _analyze_poses(self, poses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze poses for safety risks
        
        Detects:
        - Falls (person horizontal)
        - Bending/lifting risks
        - Working at height
        - Awkward postures
        """
        risks = []
        total_people = len(poses)
        
        for i, pose_data in enumerate(poses):
            pose = pose_data['keypoints']
            
            # Check for fall
            if self._is_fallen(pose):
                risks.append({
                    'person_id': i,
                    'type': 'FALL_DETECTED',
                    'severity': 'CRITICAL',
                    'confidence': 0.92,
                    'description': 'شخص ساقط - يحتاج مساعدة فورية'
                })
            
            # Check for risky bending
            elif self._is_risky_bending(pose):
                risks.append({
                    'person_id': i,
                    'type': 'UNSAFE_LIFTING',
                    'severity': 'HIGH',
                    'confidence': 0.85,
                    'description': 'وضعية رفع خطرة - خطر على الظهر'
                })
            
            # Check for working at height
            elif self._is_at_height(pose):
                risks.append({
                    'person_id': i,
                    'type': 'WORKING_AT_HEIGHT',
                    'severity': 'HIGH',
                    'confidence': 0.78,
                    'description': 'عمل على ارتفاع - تأكد من معدات الحماية'
                })
            
            # Check for awkward posture
            elif self._is_awkward_posture(pose):
                risks.append({
                    'person_id': i,
                    'type': 'AWKWARD_POSTURE',
                    'severity': 'MEDIUM',
                    'confidence': 0.73,
                    'description': 'وضعية غير صحية - خطر إصابة متكررة'
                })
        
        return {
            'total_people': total_people,
            'risks_detected': len(risks),
            'risks': risks,
            'safe_count': total_people - len(risks)
        }
    
    def _is_fallen(self, pose: Dict[str, Any]) -> bool:
        """Detect if person has fallen"""
        try:
            # Check if person is horizontal (shoulders and hips at similar height)
            if 'left_shoulder' not in pose or 'left_hip' not in pose:
                return False
            
            shoulder_y = pose['left_shoulder']['y']
            hip_y = pose['left_hip']['y']
            
            # If shoulders and hips are close in Y-axis, person might be horizontal
            vertical_diff = abs(shoulder_y - hip_y)
            
            # Also check head position
            if 'nose' in pose:
                nose_y = pose['nose']['y']
                # If head is below hips, likely fallen
                if nose_y > hip_y and vertical_diff < 50:
                    return True
            
            return vertical_diff < 30  # Very small vertical difference = horizontal
            
        except:
            return False
    
    def _is_risky_bending(self, pose: Dict[str, Any]) -> bool:
        """Detect risky bending posture"""
        try:
            if 'nose' not in pose or 'left_hip' not in pose:
                return False
            
            # Calculate angle between torso and vertical
            nose = pose['nose']
            hip = pose['left_hip']
            
            # If nose is significantly forward of hips, person is bending
            horizontal_diff = abs(nose['x'] - hip['x'])
            vertical_diff = abs(nose['y'] - hip['y'])
            
            if vertical_diff > 0:
                angle = math.degrees(math.atan(horizontal_diff / vertical_diff))
                # Bending more than 45 degrees is risky
                return angle > 45
            
            return False
            
        except:
            return False
    
    def _is_at_height(self, pose: Dict[str, Any]) -> bool:
        """Detect if person is working at height"""
        try:
            # Simple heuristic: if feet are in upper portion of image
            if 'left_ankle' not in pose:
                return False
            
            ankle_y = pose['left_ankle']['y']
            
            # Assuming image height is available, check if person is high up
            # This is simplified - real implementation would need depth info
            return ankle_y < 200  # Upper part of frame
            
        except:
            return False
    
    def _is_awkward_posture(self, pose: Dict[str, Any]) -> bool:
        """Detect awkward/uncomfortable posture"""
        try:
            # Check arm angles
            if all(k in pose for k in ['left_shoulder', 'left_elbow', 'left_wrist']):
                shoulder = pose['left_shoulder']
                elbow = pose['left_elbow']
                wrist = pose['left_wrist']
                
                # Calculate elbow angle
                angle = self._calculate_angle(shoulder, elbow, wrist)
                
                # Very bent (< 60°) or very extended (> 160°) is awkward
                if angle < 60 or angle > 160:
                    return True
            
            return False
            
        except:
            return False
    
    def _calculate_angle(self, p1: Dict, p2: Dict, p3: Dict) -> float:
        """Calculate angle between three points"""
        try:
            # Vector from p2 to p1
            v1 = (p1['x'] - p2['x'], p1['y'] - p2['y'])
            # Vector from p2 to p3
            v2 = (p3['x'] - p2['x'], p3['y'] - p2['y'])
            
            # Calculate angle
            dot = v1[0] * v2[0] + v1[1] * v2[1]
            mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
            mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
            
            if mag1 * mag2 == 0:
                return 0
            
            cos_angle = dot / (mag1 * mag2)
            cos_angle = max(-1, min(1, cos_angle))  # Clamp to [-1, 1]
            
            angle = math.degrees(math.acos(cos_angle))
            return angle
            
        except:
            return 90  # Default to neutral angle
    
    def _simulate_pose(self, image: np.ndarray) -> Dict[str, Any]:
        """Simulate pose estimation when model not available"""
        height, width = image.shape[:2]
        
        # Simulate 2-3 people
        num_people = np.random.randint(2, 4)
        poses = []
        
        for i in range(num_people):
            # Generate random pose
            base_x = np.random.randint(100, width - 100)
            base_y = np.random.randint(200, height - 100)
            
            keypoints = {
                'nose': {'x': base_x, 'y': base_y - 150, 'confidence': 0.9},
                'left_shoulder': {'x': base_x - 30, 'y': base_y - 100, 'confidence': 0.88},
                'right_shoulder': {'x': base_x + 30, 'y': base_y - 100, 'confidence': 0.87},
                'left_hip': {'x': base_x - 25, 'y': base_y, 'confidence': 0.85},
                'right_hip': {'x': base_x + 25, 'y': base_y, 'confidence': 0.86},
                'left_knee': {'x': base_x - 25, 'y': base_y + 50, 'confidence': 0.82},
                'right_knee': {'x': base_x + 25, 'y': base_y + 50, 'confidence': 0.83},
                'left_ankle': {'x': base_x - 25, 'y': base_y + 100, 'confidence': 0.80},
                'right_ankle': {'x': base_x + 25, 'y': base_y + 100, 'confidence': 0.81}
            }
            
            poses.append({
                'keypoints': keypoints,
                'avg_confidence': 0.85
            })
        
        # Simulate some risks
        risks = []
        if np.random.random() > 0.7:
            risks.append({
                'person_id': 0,
                'type': 'UNSAFE_LIFTING',
                'severity': 'HIGH',
                'confidence': 0.85,
                'description': 'وضعية رفع خطرة - خطر على الظهر'
            })
        
        return {
            'poses': poses,
            'analysis': {
                'total_people': num_people,
                'risks_detected': len(risks),
                'risks': risks,
                'safe_count': num_people - len(risks)
            },
            'timestamp': datetime.now().isoformat(),
            'simulation_mode': True
        }


# Singleton instance
_pose_estimator: Optional[PoseEstimator] = None


def get_pose_estimator(model_path: str = "yolov8n-pose.pt") -> PoseEstimator:
    """Get singleton PoseEstimator instance"""
    global _pose_estimator
    
    if _pose_estimator is None:
        _pose_estimator = PoseEstimator(model_path=model_path)
    
    return _pose_estimator
