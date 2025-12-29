"""
HAZM TUWAIQ - Frame Processor
Process camera frames with AI pipeline
"""

import cv2
import numpy as np
from typing import Dict, Any, Optional
import logging
from datetime import datetime

# Import AI engines
import sys
from pathlib import Path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from ai_core.yolo_engine import get_yolo_engine
from ai_core.pose_estimation import get_pose_estimator
from ai_core.fatigue_detection import get_fatigue_detector
from ai_core.intent_detection import get_intent_detector


class FrameProcessor:
    """
    معالج الإطارات بالذكاء الاصطناعي
    AI-powered frame processor
    """
    
    def __init__(
        self,
        enable_detection: bool = True,
        enable_pose: bool = True,
        enable_fatigue: bool = True,
        enable_intent: bool = True
    ):
        """
        Initialize frame processor
        
        Args:
            enable_detection: Enable object detection
            enable_pose: Enable pose estimation
            enable_fatigue: Enable fatigue detection
            enable_intent: Enable intent detection
        """
        self.logger = logging.getLogger(__name__)
        
        # Feature flags
        self.enable_detection = enable_detection
        self.enable_pose = enable_pose
        self.enable_fatigue = enable_fatigue
        self.enable_intent = enable_intent
        
        # Initialize AI engines
        self.yolo_engine = get_yolo_engine() if enable_detection else None
        self.pose_estimator = get_pose_estimator() if enable_pose else None
        self.fatigue_detector = get_fatigue_detector() if enable_fatigue else None
        self.intent_detector = get_intent_detector() if enable_intent else None
        
        self.logger.info("✅ Frame processor initialized")
    
    def process_frame(
        self, 
        frame: np.ndarray,
        camera_id: str,
        full_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Process single frame with AI pipeline
        
        Args:
            frame: Input frame (BGR)
            camera_id: Camera identifier
            full_analysis: Whether to run all AI engines
            
        Returns:
            Comprehensive analysis results
        """
        
        results = {
            'camera_id': camera_id,
            'timestamp': datetime.now().isoformat(),
            'frame_shape': frame.shape
        }
        
        try:
            # 1. Object Detection
            if self.enable_detection and self.yolo_engine:
                detection_results = self.yolo_engine.detect(frame, detect_ppe=True)
                results['detection'] = detection_results
            
            # 2. Pose Estimation
            if self.enable_pose and self.pose_estimator and full_analysis:
                pose_results = self.pose_estimator.estimate_pose(frame)
                results['pose'] = pose_results
            
            # 3. Fatigue Detection
            if self.enable_fatigue and self.fatigue_detector and full_analysis:
                fatigue_results = self.fatigue_detector.detect_fatigue(frame)
                results['fatigue'] = fatigue_results
            
            # 4. Intent Detection
            if self.enable_intent and self.intent_detector and full_analysis:
                # Get person positions from detection
                if 'detection' in results and results['detection'].get('people_count', 0) > 0:
                    # Use first detected person
                    for obj in results['detection'].get('objects', []):
                        if obj['class'] == 'person':
                            bbox = obj['bbox']
                            center_x = (bbox['x1'] + bbox['x2']) / 2
                            center_y = (bbox['y1'] + bbox['y2']) / 2
                            
                            intent_results = self.intent_detector.detect_intent(
                                person_position=(center_x, center_y),
                                person_pose=results.get('pose'),
                                context={'detection': results.get('detection')}
                            )
                            results['intent'] = intent_results
                            break
            
            # 5. Aggregate Safety Assessment
            results['safety_assessment'] = self._assess_safety(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Frame processing error: {e}")
            results['error'] = str(e)
            return results
    
    def _assess_safety(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate safety assessment from all analyses
        
        Args:
            analysis: Full analysis results
            
        Returns:
            Overall safety assessment
        """
        
        risks = []
        risk_score = 0
        
        # Check PPE compliance
        if 'detection' in analysis:
            ppe = analysis['detection'].get('ppe_compliance', {})
            if not ppe.get('compliant', True):
                risk_score += 30
                risks.append({
                    'type': 'PPE_VIOLATION',
                    'severity': 'HIGH',
                    'source': 'detection',
                    'details': ppe.get('violations', [])
                })
        
        # Check pose risks
        if 'pose' in analysis:
            pose_analysis = analysis['pose'].get('analysis', {})
            pose_risks = pose_analysis.get('risks', [])
            if pose_risks:
                risk_score += len(pose_risks) * 20
                for risk in pose_risks:
                    risks.append({
                        'type': risk['type'],
                        'severity': risk['severity'],
                        'source': 'pose',
                        'details': risk
                    })
        
        # Check fatigue
        if 'fatigue' in analysis:
            if analysis['fatigue'].get('fatigue_detected', False):
                fatigue_level = analysis['fatigue'].get('fatigue_level', 0)
                risk_score += fatigue_level
                risks.append({
                    'type': 'WORKER_FATIGUE',
                    'severity': analysis['fatigue'].get('level_category', 'LOW'),
                    'source': 'fatigue',
                    'details': analysis['fatigue']
                })
        
        # Check intent
        if 'intent' in analysis:
            intent_risk = analysis['intent'].get('risk_assessment', {})
            intent_score = intent_risk.get('risk_score', 0)
            if intent_score > 30:
                risk_score += intent_score
                dangerous_intents = analysis['intent'].get('dangerous_intents', [])
                for intent in dangerous_intents:
                    risks.append({
                        'type': intent['intent'],
                        'severity': intent['risk'],
                        'source': 'intent',
                        'details': intent
                    })
        
        # Determine overall level
        if risk_score >= 70:
            level = 'CRITICAL'
            message = '🚨 حالة حرجة - تدخل فوري مطلوب'
            action = 'IMMEDIATE_ACTION'
        elif risk_score >= 40:
            level = 'HIGH'
            message = '⚠️ خطر عالي - تنبيه مطلوب'
            action = 'ALERT'
        elif risk_score >= 20:
            level = 'MODERATE'
            message = '⚡ خطر متوسط - مراقبة دقيقة'
            action = 'MONITOR'
        else:
            level = 'LOW'
            message = '✅ حالة طبيعية'
            action = 'NORMAL'
        
        return {
            'overall_risk_score': risk_score,
            'risk_level': level,
            'message': message,
            'recommended_action': action,
            'risks': risks,
            'total_risks': len(risks)
        }
    
    def annotate_frame(
        self, 
        frame: np.ndarray,
        analysis: Dict[str, Any]
    ) -> np.ndarray:
        """
        Annotate frame with detection results
        
        Args:
            frame: Input frame
            analysis: Analysis results from process_frame
            
        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        
        try:
            # Draw detections
            if 'detection' in analysis:
                for obj in analysis['detection'].get('objects', []):
                    bbox = obj['bbox']
                    x1, y1 = int(bbox['x1']), int(bbox['y1'])
                    x2, y2 = int(bbox['x2']), int(bbox['y2'])
                    
                    # Color based on class
                    color = (0, 255, 0)  # Green for normal
                    if 'no_' in obj['class'].lower():
                        color = (0, 0, 255)  # Red for violations
                    
                    # Draw box
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                    
                    # Draw label
                    label = f"{obj['class']} {obj['confidence']:.2f}"
                    cv2.putText(
                        annotated, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
                    )
            
            # Draw pose keypoints
            if 'pose' in analysis:
                for pose_data in analysis['pose'].get('poses', []):
                    keypoints = pose_data['keypoints']
                    
                    # Draw keypoints
                    for name, kp in keypoints.items():
                        if kp['confidence'] > 0.5:
                            x, y = int(kp['x']), int(kp['y'])
                            cv2.circle(annotated, (x, y), 3, (255, 0, 0), -1)
            
            # Draw safety status
            safety = analysis.get('safety_assessment', {})
            level = safety.get('risk_level', 'UNKNOWN')
            
            # Color based on risk
            status_color = {
                'LOW': (0, 255, 0),
                'MODERATE': (0, 255, 255),
                'HIGH': (0, 165, 255),
                'CRITICAL': (0, 0, 255)
            }.get(level, (255, 255, 255))
            
            # Draw status banner
            cv2.rectangle(annotated, (10, 10), (300, 60), (0, 0, 0), -1)
            cv2.rectangle(annotated, (10, 10), (300, 60), status_color, 2)
            cv2.putText(
                annotated, f"Risk: {level}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2
            )
            
            return annotated
            
        except Exception as e:
            self.logger.error(f"Annotation error: {e}")
            return annotated


# Singleton instance
_frame_processor: Optional[FrameProcessor] = None


def get_frame_processor() -> FrameProcessor:
    """Get singleton FrameProcessor instance"""
    global _frame_processor
    
    if _frame_processor is None:
        _frame_processor = FrameProcessor()
    
    return _frame_processor
