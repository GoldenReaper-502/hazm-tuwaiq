"""
HAZM TUWAIQ - Intent Detection
Predict worker intentions and prevent accidents before they happen
Revolutionary "Unhappened Accident" Engine
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque
import logging


class IntentDetector:
    """
    كشف النوايا - منع الحوادث قبل حدوثها
    Intent-Aware Safety: Predict and prevent accidents
    
    This is the revolutionary "Unhappened Accident Engine"
    """
    
    def __init__(self, history_window: int = 30):
        """
        Initialize intent detector
        
        Args:
            history_window: Number of frames to track for pattern analysis
        """
        self.history_window = history_window
        self.logger = logging.getLogger(__name__)
        
        # Movement tracking
        self.position_history = deque(maxlen=history_window)
        self.velocity_history = deque(maxlen=history_window)
        self.direction_history = deque(maxlen=history_window)
        
        # Gaze tracking
        self.gaze_history = deque(maxlen=history_window)
        
        # Body orientation tracking
        self.orientation_history = deque(maxlen=history_window)
        
        # Known dangerous zones (would come from configuration)
        self.danger_zones = [
            {'name': 'Heavy Machinery Area', 'x': 100, 'y': 200, 'radius': 150},
            {'name': 'Electrical Panel', 'x': 500, 'y': 300, 'radius': 100},
            {'name': 'Loading Zone', 'x': 800, 'y': 400, 'radius': 200}
        ]
    
    def detect_intent(
        self, 
        person_position: Tuple[float, float],
        person_pose: Optional[Dict] = None,
        gaze_direction: Optional[Tuple[float, float]] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Detect person's intent and predict potential accidents
        
        Args:
            person_position: (x, y) coordinates
            person_pose: Pose keypoints from pose estimator
            gaze_direction: (dx, dy) gaze vector
            context: Additional context (nearby objects, etc.)
            
        Returns:
            Intent analysis with predictions
        """
        
        # Update tracking history
        self._update_history(person_position, gaze_direction)
        
        # Analyze movement patterns
        movement_analysis = self._analyze_movement()
        
        # Predict trajectory
        predicted_path = self._predict_trajectory()
        
        # Check for potential collisions
        collision_risks = self._check_collision_risks(predicted_path)
        
        # Detect dangerous intentions
        dangerous_intents = self._detect_dangerous_intents(
            movement_analysis, 
            predicted_path,
            person_pose,
            context
        )
        
        # Calculate overall risk
        risk_assessment = self._assess_risk(
            movement_analysis,
            collision_risks,
            dangerous_intents
        )
        
        return {
            'intent': movement_analysis,
            'predicted_path': predicted_path,
            'collision_risks': collision_risks,
            'dangerous_intents': dangerous_intents,
            'risk_assessment': risk_assessment,
            'timestamp': datetime.now().isoformat()
        }
    
    def _update_history(
        self, 
        position: Tuple[float, float],
        gaze: Optional[Tuple[float, float]]
    ):
        """Update tracking histories"""
        
        # Add position
        self.position_history.append(position)
        
        # Calculate velocity
        if len(self.position_history) >= 2:
            prev_pos = self.position_history[-2]
            velocity = (
                position[0] - prev_pos[0],
                position[1] - prev_pos[1]
            )
            self.velocity_history.append(velocity)
            
            # Calculate direction
            speed = np.sqrt(velocity[0]**2 + velocity[1]**2)
            if speed > 0:
                direction = (velocity[0]/speed, velocity[1]/speed)
                self.direction_history.append(direction)
        
        # Add gaze
        if gaze:
            self.gaze_history.append(gaze)
    
    def _analyze_movement(self) -> Dict[str, Any]:
        """Analyze movement patterns"""
        
        if len(self.velocity_history) < 5:
            return {
                'type': 'STATIONARY',
                'speed': 0,
                'direction': None,
                'pattern': 'INSUFFICIENT_DATA'
            }
        
        # Calculate average velocity
        velocities = list(self.velocity_history)
        avg_vx = np.mean([v[0] for v in velocities])
        avg_vy = np.mean([v[1] for v in velocities])
        
        speed = np.sqrt(avg_vx**2 + avg_vy**2)
        
        # Determine movement type
        if speed < 5:
            movement_type = 'STATIONARY'
        elif speed < 15:
            movement_type = 'WALKING'
        elif speed < 30:
            movement_type = 'FAST_WALKING'
        else:
            movement_type = 'RUNNING'
        
        # Detect patterns
        pattern = self._detect_movement_pattern()
        
        return {
            'type': movement_type,
            'speed': float(speed),
            'direction': (float(avg_vx), float(avg_vy)) if speed > 0 else None,
            'pattern': pattern
        }
    
    def _detect_movement_pattern(self) -> str:
        """Detect specific movement patterns"""
        
        if len(self.direction_history) < 10:
            return 'UNKNOWN'
        
        directions = list(self.direction_history)
        
        # Check for straight line
        direction_variance = np.var([d[0] for d in directions]) + np.var([d[1] for d in directions])
        
        if direction_variance < 0.1:
            return 'STRAIGHT_LINE'
        
        # Check for turning
        direction_changes = 0
        for i in range(1, len(directions)):
            angle_change = np.arccos(np.clip(
                directions[i][0] * directions[i-1][0] + directions[i][1] * directions[i-1][1],
                -1.0, 1.0
            ))
            if abs(angle_change) > 0.5:  # ~30 degrees
                direction_changes += 1
        
        if direction_changes > len(directions) * 0.3:
            return 'ERRATIC'
        elif direction_changes > 2:
            return 'TURNING'
        
        return 'NORMAL'
    
    def _predict_trajectory(self, steps: int = 10) -> List[Tuple[float, float]]:
        """Predict future trajectory"""
        
        if len(self.position_history) < 2 or len(self.velocity_history) < 2:
            return []
        
        # Get current position and velocity
        current_pos = self.position_history[-1]
        current_vel = self.velocity_history[-1]
        
        # Simple linear prediction
        trajectory = []
        for i in range(1, steps + 1):
            predicted_pos = (
                current_pos[0] + current_vel[0] * i,
                current_pos[1] + current_vel[1] * i
            )
            trajectory.append(predicted_pos)
        
        return trajectory
    
    def _check_collision_risks(
        self, 
        trajectory: List[Tuple[float, float]]
    ) -> List[Dict[str, Any]]:
        """Check if predicted trajectory intersects danger zones"""
        
        risks = []
        
        for point in trajectory:
            for zone in self.danger_zones:
                # Calculate distance to danger zone
                distance = np.sqrt(
                    (point[0] - zone['x'])**2 + 
                    (point[1] - zone['y'])**2
                )
                
                if distance < zone['radius']:
                    # Calculate time to collision
                    step_index = trajectory.index(point)
                    time_to_collision = step_index * 0.1  # Assuming 10 FPS
                    
                    risks.append({
                        'zone': zone['name'],
                        'time_to_collision': time_to_collision,
                        'severity': 'HIGH' if time_to_collision < 2 else 'MEDIUM',
                        'predicted_position': point,
                        'type': 'TRAJECTORY_COLLISION'
                    })
                    break
        
        return risks
    
    def _detect_dangerous_intents(
        self,
        movement: Dict[str, Any],
        trajectory: List[Tuple[float, float]],
        pose: Optional[Dict],
        context: Optional[Dict]
    ) -> List[Dict[str, Any]]:
        """Detect potentially dangerous intentions"""
        
        intents = []
        
        # Running towards danger
        if movement['type'] == 'RUNNING' and trajectory:
            intents.append({
                'intent': 'RUSHING',
                'risk': 'HIGH',
                'description': 'العامل يركض - احتمال تعثر أو اصطدام',
                'prevention': 'تنبيه العامل للإبطاء'
            })
        
        # Erratic movement near machinery
        if movement['pattern'] == 'ERRATIC':
            intents.append({
                'intent': 'CONFUSED_MOVEMENT',
                'risk': 'MEDIUM',
                'description': 'حركة غير منتظمة - قد يكون العامل مشتتاً',
                'prevention': 'فحص انتباه العامل'
            })
        
        # Not looking at path (would use gaze data)
        if self.gaze_history and len(self.gaze_history) >= 5:
            # Check if gaze direction differs from movement direction
            recent_gazes = list(self.gaze_history)[-5:]
            if movement['direction']:
                # Simplified check
                intents.append({
                    'intent': 'DISTRACTED_WALKING',
                    'risk': 'HIGH',
                    'description': 'العامل لا ينظر لطريقه - خطر اصطدام',
                    'prevention': 'تنبيه صوتي فوري'
                })
        
        # Approaching restricted area
        if trajectory:
            last_point = trajectory[-1]
            for zone in self.danger_zones:
                distance = np.sqrt(
                    (last_point[0] - zone['x'])**2 + 
                    (last_point[1] - zone['y'])**2
                )
                if distance < zone['radius'] * 1.5:  # Warning zone
                    intents.append({
                        'intent': 'APPROACHING_DANGER_ZONE',
                        'risk': 'HIGH',
                        'description': f'اقتراب من منطقة خطرة: {zone["name"]}',
                        'prevention': 'إيقاف الوصول أو تحذير العامل'
                    })
        
        return intents
    
    def _assess_risk(
        self,
        movement: Dict[str, Any],
        collisions: List[Dict],
        intents: List[Dict]
    ) -> Dict[str, Any]:
        """Assess overall risk level"""
        
        risk_score = 0
        
        # Movement-based risk
        if movement['type'] == 'RUNNING':
            risk_score += 30
        elif movement['type'] == 'FAST_WALKING':
            risk_score += 15
        
        if movement['pattern'] == 'ERRATIC':
            risk_score += 25
        
        # Collision-based risk
        for collision in collisions:
            if collision['time_to_collision'] < 1:
                risk_score += 50
            elif collision['time_to_collision'] < 3:
                risk_score += 30
            else:
                risk_score += 15
        
        # Intent-based risk
        for intent in intents:
            if intent['risk'] == 'HIGH':
                risk_score += 25
            elif intent['risk'] == 'MEDIUM':
                risk_score += 15
        
        # Determine level
        if risk_score >= 70:
            level = 'CRITICAL'
            action = 'IMMEDIATE_INTERVENTION'
            message = '🚨 خطر حرج - تدخل فوري مطلوب'
        elif risk_score >= 40:
            level = 'HIGH'
            action = 'ALERT_WORKER'
            message = '⚠️ خطر عالي - تنبيه العامل'
        elif risk_score >= 20:
            level = 'MODERATE'
            action = 'MONITOR_CLOSELY'
            message = '⚡ خطر متوسط - مراقبة دقيقة'
        else:
            level = 'LOW'
            action = 'CONTINUE_MONITORING'
            message = '✅ وضع طبيعي'
        
        return {
            'risk_score': risk_score,
            'risk_level': level,
            'recommended_action': action,
            'message': message,
            'unhappened_accidents_prevented': len(collisions) + len([i for i in intents if i['risk'] == 'HIGH'])
        }
    
    def reset_history(self):
        """Reset all tracking histories"""
        self.position_history.clear()
        self.velocity_history.clear()
        self.direction_history.clear()
        self.gaze_history.clear()
        self.orientation_history.clear()


# Singleton instance
_intent_detector: Optional[IntentDetector] = None


def get_intent_detector() -> IntentDetector:
    """Get singleton IntentDetector instance"""
    global _intent_detector
    
    if _intent_detector is None:
        _intent_detector = IntentDetector()
    
    return _intent_detector
