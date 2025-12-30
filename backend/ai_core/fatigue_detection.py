"""
HAZM TUWAIQ - Fatigue Detection
Detect worker fatigue through facial analysis and body language
"""

import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from collections import deque


def _get_cv2():
    """Lazy import cv2 to prevent startup crashes"""
    try:
        import cv2
        return cv2
    except ImportError as e:
        raise RuntimeError(f"OpenCV not available: {e}")


try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False


class FatigueDetector:
    """
    كشف الإرهاق من خلال تحليل الوجه ولغة الجسد
    Fatigue detection through facial and body language analysis
    """
    
    def __init__(self):
        """Initialize fatigue detector"""
        self.logger = logging.getLogger(__name__)
        
        # Fatigue indicators thresholds
        self.EYE_CLOSURE_THRESHOLD = 0.2  # Eye aspect ratio
        self.YAWN_THRESHOLD = 0.6  # Mouth aspect ratio
        self.HEAD_NOD_THRESHOLD = 15  # Degrees
        
        # Tracking windows (last N frames)
        self.blink_history = deque(maxlen=100)  # Last 100 frames
        self.yawn_history = deque(maxlen=100)
        self.posture_history = deque(maxlen=50)
        
        # Initialize MediaPipe if available
        self.face_mesh = None
        if MEDIAPIPE_AVAILABLE:
            try:
                mp_face_mesh = mp.solutions.face_mesh
                self.face_mesh = mp_face_mesh.FaceMesh(
                    max_num_faces=5,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                self.logger.info("✅ MediaPipe Face Mesh initialized")
            except Exception as e:
                self.logger.warning(f"MediaPipe initialization failed: {e}")
    
    def detect_fatigue(self, image: np.ndarray, person_id: int = 0) -> Dict[str, Any]:
        """
        Detect fatigue indicators in image
        
        Args:
            image: Input image (BGR)
            person_id: ID of person to track
            
        Returns:
            Fatigue analysis results
        """
        if self.face_mesh is None:
            return self._simulate_fatigue()
        
        try:
            cv2 = _get_cv2()  # Lazy import
            # Convert to RGB for MediaPipe
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process image
            results = self.face_mesh.process(image_rgb)
            
            if not results.multi_face_landmarks:
                return {
                    'fatigue_detected': False,
                    'fatigue_level': 0,
                    'indicators': [],
                    'message': 'لا يوجد وجوه مكتشفة',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Analyze first face (or specified person)
            face_landmarks = results.multi_face_landmarks[0]
            
            # Calculate fatigue indicators
            indicators = self._analyze_face(face_landmarks, image.shape)
            
            # Calculate overall fatigue level
            fatigue_analysis = self._calculate_fatigue_level(indicators)
            
            return fatigue_analysis
            
        except Exception as e:
            self.logger.error(f"Fatigue detection error: {e}")
            return self._simulate_fatigue()
    
    def _analyze_face(self, landmarks, image_shape) -> Dict[str, Any]:
        """Analyze facial landmarks for fatigue indicators"""
        
        indicators = {
            'eye_closure': False,
            'yawning': False,
            'head_nodding': False,
            'slow_blinking': False,
            'details': {}
        }
        
        # Calculate Eye Aspect Ratio (EAR)
        ear = self._calculate_eye_aspect_ratio(landmarks)
        if ear < self.EYE_CLOSURE_THRESHOLD:
            indicators['eye_closure'] = True
            self.blink_history.append(1)
        else:
            self.blink_history.append(0)
        
        indicators['details']['eye_aspect_ratio'] = ear
        
        # Calculate Mouth Aspect Ratio (MAR) for yawning
        mar = self._calculate_mouth_aspect_ratio(landmarks)
        if mar > self.YAWN_THRESHOLD:
            indicators['yawning'] = True
            self.yawn_history.append(1)
        else:
            self.yawn_history.append(0)
        
        indicators['details']['mouth_aspect_ratio'] = mar
        
        # Check blink frequency
        if len(self.blink_history) >= 100:
            blink_rate = sum(self.blink_history) / len(self.blink_history)
            if blink_rate > 0.15:  # More than 15% of frames with eyes closed
                indicators['slow_blinking'] = True
            indicators['details']['blink_rate'] = blink_rate
        
        # Check yawn frequency
        if len(self.yawn_history) >= 100:
            yawn_rate = sum(self.yawn_history) / len(self.yawn_history)
            if yawn_rate > 0.05:  # More than 5% of frames yawning
                indicators['details']['yawn_frequency'] = 'high'
        
        return indicators
    
    def _calculate_eye_aspect_ratio(self, landmarks) -> float:
        """
        Calculate Eye Aspect Ratio (EAR)
        EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
        """
        try:
            # Left eye landmarks (simplified)
            # MediaPipe face mesh has 468 landmarks
            # Eye landmarks: 33, 133, 160, 158, 144, 153
            
            left_eye = [33, 160, 158, 133, 153, 144]
            
            # Get landmark coordinates
            def get_coords(idx):
                lm = landmarks.landmark[idx]
                return (lm.x, lm.y)
            
            # Calculate vertical distances
            p2 = get_coords(left_eye[1])
            p6 = get_coords(left_eye[5])
            p3 = get_coords(left_eye[2])
            p5 = get_coords(left_eye[4])
            
            vertical1 = np.linalg.norm(np.array(p2) - np.array(p6))
            vertical2 = np.linalg.norm(np.array(p3) - np.array(p5))
            
            # Calculate horizontal distance
            p1 = get_coords(left_eye[0])
            p4 = get_coords(left_eye[3])
            horizontal = np.linalg.norm(np.array(p1) - np.array(p4))
            
            # EAR
            if horizontal == 0:
                return 0.3
            
            ear = (vertical1 + vertical2) / (2.0 * horizontal)
            return ear
            
        except:
            return 0.3  # Default neutral value
    
    def _calculate_mouth_aspect_ratio(self, landmarks) -> float:
        """Calculate Mouth Aspect Ratio (MAR) for yawn detection"""
        try:
            # Mouth landmarks: 61, 291, 81, 178
            mouth = [61, 81, 13, 14, 78, 308]
            
            def get_coords(idx):
                lm = landmarks.landmark[idx]
                return (lm.x, lm.y)
            
            # Vertical distance (mouth opening)
            p1 = get_coords(13)  # Upper lip
            p2 = get_coords(14)  # Lower lip
            vertical = np.linalg.norm(np.array(p1) - np.array(p2))
            
            # Horizontal distance (mouth width)
            p3 = get_coords(61)  # Left corner
            p4 = get_coords(291)  # Right corner
            horizontal = np.linalg.norm(np.array(p3) - np.array(p4))
            
            if horizontal == 0:
                return 0.3
            
            mar = vertical / horizontal
            return mar
            
        except:
            return 0.3
    
    def _calculate_fatigue_level(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall fatigue level from indicators"""
        
        fatigue_score = 0
        detected_indicators = []
        
        # Check each indicator
        if indicators['eye_closure']:
            fatigue_score += 30
            detected_indicators.append({
                'type': 'EYE_CLOSURE',
                'severity': 'HIGH',
                'description': 'عيون مغلقة - علامة إرهاق واضحة'
            })
        
        if indicators['yawning']:
            fatigue_score += 25
            detected_indicators.append({
                'type': 'YAWNING',
                'severity': 'MEDIUM',
                'description': 'تثاؤب متكرر - علامة تعب'
            })
        
        if indicators['slow_blinking']:
            fatigue_score += 20
            detected_indicators.append({
                'type': 'SLOW_BLINKING',
                'severity': 'MEDIUM',
                'description': 'رمش بطيء - قد يشير للنعاس'
            })
        
        if indicators.get('head_nodding', False):
            fatigue_score += 15
            detected_indicators.append({
                'type': 'HEAD_NODDING',
                'severity': 'LOW',
                'description': 'حركة رأس غير منتظمة'
            })
        
        # Determine fatigue level
        if fatigue_score >= 50:
            level = 'CRITICAL'
            message = '🚨 إرهاق حرج - يجب إيقاف العمل فوراً'
            action = 'IMMEDIATE_BREAK'
        elif fatigue_score >= 30:
            level = 'HIGH'
            message = '⚠️ إرهاق عالي - يُنصح بأخذ استراحة'
            action = 'SUGGEST_BREAK'
        elif fatigue_score >= 15:
            level = 'MODERATE'
            message = '⚡ إرهاق متوسط - مراقبة مستمرة'
            action = 'MONITOR'
        else:
            level = 'LOW'
            message = '✅ حالة طبيعية'
            action = 'NONE'
        
        return {
            'fatigue_detected': fatigue_score > 0,
            'fatigue_level': fatigue_score,
            'level_category': level,
            'indicators': detected_indicators,
            'message': message,
            'recommended_action': action,
            'details': indicators.get('details', {}),
            'timestamp': datetime.now().isoformat()
        }
    
    def _simulate_fatigue(self) -> Dict[str, Any]:
        """Simulate fatigue detection when MediaPipe not available"""
        
        # Random fatigue level
        fatigue_level = np.random.choice([0, 15, 35, 60], p=[0.6, 0.2, 0.15, 0.05])
        
        indicators = []
        
        if fatigue_level >= 30:
            indicators.append({
                'type': 'EYE_CLOSURE',
                'severity': 'HIGH',
                'description': 'عيون مغلقة - علامة إرهاق واضحة'
            })
        
        if fatigue_level >= 50:
            indicators.append({
                'type': 'YAWNING',
                'severity': 'MEDIUM',
                'description': 'تثاؤب متكرر - علامة تعب'
            })
        
        if fatigue_level >= 50:
            level = 'CRITICAL'
            message = '🚨 إرهاق حرج - يجب إيقاف العمل فوراً'
            action = 'IMMEDIATE_BREAK'
        elif fatigue_level >= 30:
            level = 'HIGH'
            message = '⚠️ إرهاق عالي - يُنصح بأخذ استراحة'
            action = 'SUGGEST_BREAK'
        elif fatigue_level >= 15:
            level = 'MODERATE'
            message = '⚡ إرهاق متوسط - مراقبة مستمرة'
            action = 'MONITOR'
        else:
            level = 'LOW'
            message = '✅ حالة طبيعية'
            action = 'NONE'
        
        return {
            'fatigue_detected': fatigue_level > 0,
            'fatigue_level': fatigue_level,
            'level_category': level,
            'indicators': indicators,
            'message': message,
            'recommended_action': action,
            'details': {
                'eye_aspect_ratio': 0.25 if fatigue_level >= 30 else 0.35,
                'mouth_aspect_ratio': 0.65 if fatigue_level >= 50 else 0.30,
                'blink_rate': 0.18 if fatigue_level >= 30 else 0.08
            },
            'timestamp': datetime.now().isoformat(),
            'simulation_mode': True
        }


# Singleton instance
_fatigue_detector: Optional[FatigueDetector] = None


def get_fatigue_detector() -> FatigueDetector:
    """Get singleton FatigueDetector instance"""
    global _fatigue_detector
    
    if _fatigue_detector is None:
        _fatigue_detector = FatigueDetector()
    
    return _fatigue_detector
