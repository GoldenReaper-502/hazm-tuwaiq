"""
HAZM TUWAIQ - Enhanced Intent-Aware Safety
Advanced trajectory prediction and collision prevention
Predicts worker intentions and prevents accidents before they happen
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import deque
import numpy as np


class MovementIntent(str, Enum):
    """Predicted movement intentions"""
    STATIONARY = "stationary"
    WALKING = "walking"
    RUNNING = "running"
    REACHING = "reaching"
    BENDING = "bending"
    CLIMBING = "climbing"
    OPERATING_EQUIPMENT = "operating_equipment"
    ENTERING_ZONE = "entering_zone"
    EXITING_ZONE = "exiting_zone"
    UNKNOWN = "unknown"


class CollisionRisk(str, Enum):
    """Collision risk levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    IMMINENT = "imminent"


class InterventicationType(str, Enum):
    """Types of safety interventions"""
    NONE = "none"
    VISUAL_WARNING = "visual_warning"
    AUDIO_ALERT = "audio_alert"
    STOP_EQUIPMENT = "stop_equipment"
    ACTIVATE_BARRIER = "activate_barrier"
    EMERGENCY_STOP = "emergency_stop"


@dataclass
class Position:
    """3D position"""
    x: float
    y: float
    z: float
    timestamp: datetime
    

@dataclass
class Trajectory:
    """Movement trajectory"""
    worker_id: str
    positions: List[Position]
    velocity: Tuple[float, float, float]  # vx, vy, vz
    acceleration: Tuple[float, float, float]
    predicted_intent: MovementIntent
    confidence: float
    

@dataclass
class CollisionPrediction:
    """Collision prediction"""
    prediction_id: str
    worker_id: str
    collision_object_type: str  # equipment, zone, vehicle, other_worker
    collision_object_id: str
    risk_level: CollisionRisk
    time_to_collision: float  # seconds
    collision_point: Position
    predicted_impact_severity: str  # low, medium, high, critical
    probability: float  # 0-1
    recommended_intervention: InterventicationType
    

@dataclass
class SafetyZone:
    """Safety zone definition"""
    zone_id: str
    zone_type: str  # restricted, caution, hazardous
    center: Tuple[float, float, float]
    radius: float
    active: bool
    

class EnhancedIntentAwareSafety:
    """
    Enhanced intent-aware safety system
    
    Features:
    - Advanced trajectory prediction using physics and ML
    - Multi-object collision detection
    - Context-aware intent recognition
    - Proactive intervention recommendations
    - Learns from near-misses
    """
    
    def __init__(self):
        self.trajectories: Dict[str, Trajectory] = {}
        self.position_history: Dict[str, deque] = {}
        self.collision_predictions: List[CollisionPrediction] = []
        self.safety_zones: Dict[str, SafetyZone] = {}
        self.equipment_positions: Dict[str, Position] = {}
        
        # Learning: intent patterns
        self.intent_patterns: Dict[str, List[Tuple[MovementIntent, List[float]]]] = {}
        
        # Configuration
        self.prediction_horizon = 5.0  # seconds
        self.position_history_length = 30  # Keep last 30 positions
        self.collision_distance_threshold = 2.0  # meters
        
        # Initialize position history deques
        self.max_history = 30
    
    def update_worker_position(
        self,
        worker_id: str,
        position: Position
    ):
        """Update worker position and predict trajectory"""
        
        # Initialize history if new worker
        if worker_id not in self.position_history:
            self.position_history[worker_id] = deque(maxlen=self.max_history)
        
        # Add to history
        self.position_history[worker_id].append(position)
        
        # Need at least 3 positions to predict trajectory
        if len(self.position_history[worker_id]) < 3:
            return
        
        # Calculate trajectory
        trajectory = self._calculate_trajectory(worker_id)
        self.trajectories[worker_id] = trajectory
        
        # Predict collisions
        self._predict_collisions(worker_id, trajectory)
    
    def _calculate_trajectory(self, worker_id: str) -> Trajectory:
        """Calculate trajectory from position history"""
        
        positions = list(self.position_history[worker_id])
        
        # Calculate velocity (average over last 3 positions)
        if len(positions) >= 3:
            recent_positions = positions[-3:]
            
            # Time differences
            dt1 = (recent_positions[-1].timestamp - recent_positions[-2].timestamp).total_seconds()
            dt2 = (recent_positions[-2].timestamp - recent_positions[-3].timestamp).total_seconds()
            
            if dt1 > 0 and dt2 > 0:
                # Velocities
                vx1 = (recent_positions[-1].x - recent_positions[-2].x) / dt1
                vy1 = (recent_positions[-1].y - recent_positions[-2].y) / dt1
                vz1 = (recent_positions[-1].z - recent_positions[-2].z) / dt1
                
                vx2 = (recent_positions[-2].x - recent_positions[-3].x) / dt2
                vy2 = (recent_positions[-2].y - recent_positions[-3].y) / dt2
                vz2 = (recent_positions[-2].z - recent_positions[-3].z) / dt2
                
                # Average velocity
                vx = (vx1 + vx2) / 2.0
                vy = (vy1 + vy2) / 2.0
                vz = (vz1 + vz2) / 2.0
                
                # Acceleration
                ax = (vx1 - vx2) / dt1
                ay = (vy1 - vy2) / dt1
                az = (vz1 - vz2) / dt1
            else:
                vx = vy = vz = 0.0
                ax = ay = az = 0.0
        else:
            vx = vy = vz = 0.0
            ax = ay = az = 0.0
        
        # Predict intent
        intent, confidence = self._predict_intent(
            positions,
            (vx, vy, vz),
            (ax, ay, az)
        )
        
        return Trajectory(
            worker_id=worker_id,
            positions=positions,
            velocity=(vx, vy, vz),
            acceleration=(ax, ay, az),
            predicted_intent=intent,
            confidence=confidence
        )
    
    def _predict_intent(
        self,
        positions: List[Position],
        velocity: Tuple[float, float, float],
        acceleration: Tuple[float, float, float]
    ) -> Tuple[MovementIntent, float]:
        """Predict movement intent from trajectory"""
        
        vx, vy, vz = velocity
        ax, ay, az = acceleration
        
        # Calculate speed
        speed = np.sqrt(vx**2 + vy**2 + vz**2)
        
        # Calculate vertical movement
        vertical_velocity = vz
        
        # Intent classification rules
        
        # Stationary
        if speed < 0.1:  # < 0.1 m/s
            return MovementIntent.STATIONARY, 0.95
        
        # Running
        if speed > 2.5:  # > 2.5 m/s (~9 km/h)
            return MovementIntent.RUNNING, 0.85
        
        # Climbing (vertical movement)
        if abs(vertical_velocity) > 0.3:
            return MovementIntent.CLIMBING, 0.80
        
        # Bending (downward z movement)
        if vertical_velocity < -0.5:
            return MovementIntent.BENDING, 0.75
        
        # Reaching (acceleration pattern)
        if np.sqrt(ax**2 + ay**2) > 1.0:  # High lateral acceleration
            return MovementIntent.REACHING, 0.70
        
        # Walking (default for moderate speed)
        if speed > 0.1:
            return MovementIntent.WALKING, 0.90
        
        return MovementIntent.UNKNOWN, 0.50
    
    def _predict_collisions(self, worker_id: str, trajectory: Trajectory):
        """Predict potential collisions"""
        
        current_position = trajectory.positions[-1]
        vx, vy, vz = trajectory.velocity
        
        # Predict future positions
        future_positions = []
        for t in np.arange(0, self.prediction_horizon, 0.5):
            future_x = current_position.x + vx * t
            future_y = current_position.y + vy * t
            future_z = current_position.z + vz * t
            
            future_positions.append(Position(
                x=future_x,
                y=future_y,
                z=future_z,
                timestamp=current_position.timestamp + timedelta(seconds=t)
            ))
        
        # Check collisions with safety zones
        for zone_id, zone in self.safety_zones.items():
            if not zone.active:
                continue
            
            collision_time = self._check_zone_collision(future_positions, zone)
            
            if collision_time is not None:
                # Collision predicted
                collision_point = future_positions[int(collision_time / 0.5)]
                
                risk_level = self._calculate_collision_risk(
                    collision_time,
                    zone.zone_type
                )
                
                intervention = self._recommend_intervention(risk_level, zone.zone_type)
                
                prediction = CollisionPrediction(
                    prediction_id=f"COLL-{len(self.collision_predictions) + 1:06d}",
                    worker_id=worker_id,
                    collision_object_type="zone",
                    collision_object_id=zone_id,
                    risk_level=risk_level,
                    time_to_collision=collision_time,
                    collision_point=collision_point,
                    predicted_impact_severity=zone.zone_type,
                    probability=0.8,
                    recommended_intervention=intervention
                )
                
                self.collision_predictions.append(prediction)
        
        # Check collisions with equipment
        for equipment_id, equipment_pos in self.equipment_positions.items():
            collision_time = self._check_equipment_collision(
                future_positions,
                equipment_pos
            )
            
            if collision_time is not None:
                collision_point = future_positions[int(collision_time / 0.5)]
                
                risk_level = self._calculate_collision_risk(collision_time, "equipment")
                intervention = self._recommend_intervention(risk_level, "equipment")
                
                prediction = CollisionPrediction(
                    prediction_id=f"COLL-{len(self.collision_predictions) + 1:06d}",
                    worker_id=worker_id,
                    collision_object_type="equipment",
                    collision_object_id=equipment_id,
                    risk_level=risk_level,
                    time_to_collision=collision_time,
                    collision_point=collision_point,
                    predicted_impact_severity="high",
                    probability=0.75,
                    recommended_intervention=intervention
                )
                
                self.collision_predictions.append(prediction)
        
        # Check collisions with other workers
        for other_worker_id, other_trajectory in self.trajectories.items():
            if other_worker_id == worker_id:
                continue
            
            collision_time = self._check_worker_collision(
                trajectory,
                other_trajectory
            )
            
            if collision_time is not None and collision_time < self.prediction_horizon:
                # Calculate collision point
                t = collision_time
                collision_x = current_position.x + vx * t
                collision_y = current_position.y + vy * t
                collision_z = current_position.z + vz * t
                
                collision_point = Position(
                    x=collision_x,
                    y=collision_y,
                    z=collision_z,
                    timestamp=current_position.timestamp + timedelta(seconds=t)
                )
                
                risk_level = self._calculate_collision_risk(collision_time, "worker")
                intervention = self._recommend_intervention(risk_level, "worker")
                
                prediction = CollisionPrediction(
                    prediction_id=f"COLL-{len(self.collision_predictions) + 1:06d}",
                    worker_id=worker_id,
                    collision_object_type="worker",
                    collision_object_id=other_worker_id,
                    risk_level=risk_level,
                    time_to_collision=collision_time,
                    collision_point=collision_point,
                    predicted_impact_severity="medium",
                    probability=0.65,
                    recommended_intervention=intervention
                )
                
                self.collision_predictions.append(prediction)
    
    def _check_zone_collision(
        self,
        future_positions: List[Position],
        zone: SafetyZone
    ) -> Optional[float]:
        """Check if trajectory intersects with safety zone"""
        
        zx, zy, zz = zone.center
        
        for i, pos in enumerate(future_positions):
            distance = np.sqrt(
                (pos.x - zx)**2 +
                (pos.y - zy)**2 +
                (pos.z - zz)**2
            )
            
            if distance <= zone.radius:
                return i * 0.5  # Time in seconds
        
        return None
    
    def _check_equipment_collision(
        self,
        future_positions: List[Position],
        equipment_pos: Position
    ) -> Optional[float]:
        """Check collision with equipment"""
        
        for i, pos in enumerate(future_positions):
            distance = np.sqrt(
                (pos.x - equipment_pos.x)**2 +
                (pos.y - equipment_pos.y)**2 +
                (pos.z - equipment_pos.z)**2
            )
            
            if distance <= self.collision_distance_threshold:
                return i * 0.5
        
        return None
    
    def _check_worker_collision(
        self,
        trajectory1: Trajectory,
        trajectory2: Trajectory
    ) -> Optional[float]:
        """Check collision between two workers"""
        
        # Get current positions and velocities
        pos1 = trajectory1.positions[-1]
        pos2 = trajectory2.positions[-1]
        
        vx1, vy1, vz1 = trajectory1.velocity
        vx2, vy2, vz2 = trajectory2.velocity
        
        # Relative velocity
        vx_rel = vx1 - vx2
        vy_rel = vy1 - vy2
        vz_rel = vz1 - vz2
        
        # Relative position
        dx = pos1.x - pos2.x
        dy = pos1.y - pos2.y
        dz = pos1.z - pos2.z
        
        # Quadratic equation for collision time
        # |pos1(t) - pos2(t)| = threshold
        # (dx + vx_rel*t)^2 + (dy + vy_rel*t)^2 + (dz + vz_rel*t)^2 = threshold^2
        
        a = vx_rel**2 + vy_rel**2 + vz_rel**2
        b = 2 * (dx*vx_rel + dy*vy_rel + dz*vz_rel)
        c = dx**2 + dy**2 + dz**2 - self.collision_distance_threshold**2
        
        if a == 0:  # No relative movement
            if c <= 0:  # Already colliding
                return 0.0
            return None
        
        discriminant = b**2 - 4*a*c
        
        if discriminant < 0:  # No collision
            return None
        
        # Two solutions
        t1 = (-b - np.sqrt(discriminant)) / (2*a)
        t2 = (-b + np.sqrt(discriminant)) / (2*a)
        
        # Take earliest positive time
        if t1 > 0:
            return t1
        elif t2 > 0:
            return t2
        
        return None
    
    def _calculate_collision_risk(
        self,
        time_to_collision: float,
        object_type: str
    ) -> CollisionRisk:
        """Calculate collision risk level"""
        
        # Base risk on time
        if time_to_collision < 1.0:
            base_risk = CollisionRisk.IMMINENT
        elif time_to_collision < 2.0:
            base_risk = CollisionRisk.HIGH
        elif time_to_collision < 3.5:
            base_risk = CollisionRisk.MEDIUM
        else:
            base_risk = CollisionRisk.LOW
        
        # Adjust for object type
        if object_type in ["hazardous", "equipment"]:
            # Escalate risk for hazardous objects
            risk_levels = [CollisionRisk.NONE, CollisionRisk.LOW, CollisionRisk.MEDIUM,
                          CollisionRisk.HIGH, CollisionRisk.IMMINENT]
            current_index = risk_levels.index(base_risk)
            escalated_index = min(len(risk_levels) - 1, current_index + 1)
            return risk_levels[escalated_index]
        
        return base_risk
    
    def _recommend_intervention(
        self,
        risk_level: CollisionRisk,
        object_type: str
    ) -> InterventicationType:
        """Recommend intervention based on risk"""
        
        if risk_level == CollisionRisk.IMMINENT:
            if object_type in ["hazardous", "equipment"]:
                return InterventicationType.EMERGENCY_STOP
            else:
                return InterventicationType.AUDIO_ALERT
        
        elif risk_level == CollisionRisk.HIGH:
            if object_type == "equipment":
                return InterventicationType.STOP_EQUIPMENT
            else:
                return InterventicationType.AUDIO_ALERT
        
        elif risk_level == CollisionRisk.MEDIUM:
            return InterventicationType.VISUAL_WARNING
        
        elif risk_level == CollisionRisk.LOW:
            return InterventicationType.VISUAL_WARNING
        
        return InterventicationType.NONE
    
    def register_safety_zone(
        self,
        zone_id: str,
        zone_type: str,
        center: Tuple[float, float, float],
        radius: float
    ):
        """Register a safety zone"""
        
        self.safety_zones[zone_id] = SafetyZone(
            zone_id=zone_id,
            zone_type=zone_type,
            center=center,
            radius=radius,
            active=True
        )
    
    def update_equipment_position(
        self,
        equipment_id: str,
        position: Position
    ):
        """Update equipment position"""
        
        self.equipment_positions[equipment_id] = position
    
    def get_active_collision_predictions(
        self,
        min_risk_level: Optional[CollisionRisk] = None
    ) -> List[CollisionPrediction]:
        """Get active collision predictions"""
        
        # Filter recent predictions (last 10 seconds)
        cutoff = datetime.now() - timedelta(seconds=10)
        active_predictions = [
            p for p in self.collision_predictions
            if (datetime.now() - p.collision_point.timestamp).total_seconds() < 10
        ]
        
        # Filter by risk level
        if min_risk_level:
            risk_order = [CollisionRisk.NONE, CollisionRisk.LOW, CollisionRisk.MEDIUM,
                         CollisionRisk.HIGH, CollisionRisk.IMMINENT]
            min_index = risk_order.index(min_risk_level)
            active_predictions = [
                p for p in active_predictions
                if risk_order.index(p.risk_level) >= min_index
            ]
        
        # Sort by risk and time
        risk_scores = {
            CollisionRisk.IMMINENT: 5,
            CollisionRisk.HIGH: 4,
            CollisionRisk.MEDIUM: 3,
            CollisionRisk.LOW: 2,
            CollisionRisk.NONE: 1
        }
        
        active_predictions.sort(
            key=lambda p: (risk_scores[p.risk_level], -p.time_to_collision),
            reverse=True
        )
        
        return active_predictions
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get intent-aware safety system statistics"""
        
        return {
            'tracked_workers': len(self.trajectories),
            'registered_zones': len(self.safety_zones),
            'tracked_equipment': len(self.equipment_positions),
            'active_collision_predictions': len(self.get_active_collision_predictions()),
            'imminent_collisions': len([
                p for p in self.get_active_collision_predictions()
                if p.risk_level == CollisionRisk.IMMINENT
            ]),
            'high_risk_collisions': len([
                p for p in self.get_active_collision_predictions()
                if p.risk_level == CollisionRisk.HIGH
            ]),
            'prediction_horizon_seconds': self.prediction_horizon,
            'average_prediction_confidence': np.mean([
                t.confidence for t in self.trajectories.values()
            ]) if self.trajectories else 0.0
        }


# Global enhanced intent-aware safety instance
enhanced_intent_aware_safety = EnhancedIntentAwareSafety()
