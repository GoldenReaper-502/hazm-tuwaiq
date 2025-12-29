"""
HAZM TUWAIQ - Behavioral Pattern Recognition
Deep learning-based behavioral analysis for safety prediction
Recognizes complex patterns in worker behavior to predict risks
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, Counter
import numpy as np


class BehaviorCategory(str, Enum):
    """Categories of worker behavior"""
    SAFE = "safe"
    AT_RISK = "at_risk"
    UNSAFE = "unsafe"
    VIOLATION = "violation"
    FATIGUE = "fatigue"
    DISTRACTED = "distracted"
    RUSHING = "rushing"
    COMPLACENT = "complacent"


class BehaviorType(str, Enum):
    """Specific behavior types"""
    PPE_COMPLIANCE = "ppe_compliance"
    SAFETY_PROCEDURE = "safety_procedure"
    WORK_PACE = "work_pace"
    ATTENTION_LEVEL = "attention_level"
    TOOL_USAGE = "tool_usage"
    MOVEMENT_PATTERN = "movement_pattern"
    INTERACTION = "interaction"
    ZONE_COMPLIANCE = "zone_compliance"


@dataclass
class BehaviorObservation:
    """Single behavior observation"""
    observation_id: str
    worker_id: str
    timestamp: datetime
    behavior_type: BehaviorType
    category: BehaviorCategory
    confidence: float  # 0-1
    location: str
    context: Dict[str, Any]
    risk_score: float = 0.0  # 0-100
    

@dataclass
class BehaviorPattern:
    """Recognized behavioral pattern"""
    pattern_id: str
    worker_id: str
    pattern_type: str
    description: str
    frequency: int  # Occurrences
    first_seen: datetime
    last_seen: datetime
    risk_level: str
    predictive_indicators: List[str]
    recommended_intervention: str
    confidence: float = 0.0


@dataclass
class WorkerProfile:
    """Behavioral profile for a worker"""
    worker_id: str
    name: str
    observations_count: int
    safe_behaviors: int
    unsafe_behaviors: int
    violations: int
    average_risk_score: float
    behavior_trends: Dict[str, float]
    risk_patterns: List[str]
    strengths: List[str]
    areas_of_concern: List[str]
    last_updated: datetime


class BehavioralPatternRecognition:
    """
    Advanced behavioral pattern recognition system
    
    Features:
    - Real-time behavior observation tracking
    - Pattern mining across temporal and contextual dimensions
    - Worker behavioral profiling
    - Risk prediction based on behavior patterns
    - Fatigue and distraction detection
    - Intervention recommendation
    """
    
    def __init__(self):
        self.observations: List[BehaviorObservation] = []
        self.patterns: List[BehaviorPattern] = []
        self.worker_profiles: Dict[str, WorkerProfile] = {}
        self.behavior_sequences: Dict[str, List[BehaviorObservation]] = defaultdict(list)
        
        # Pattern detection thresholds
        self.pattern_thresholds = {
            'minimum_occurrences': 3,
            'time_window_hours': 24,
            'sequence_similarity': 0.7,
            'risk_threshold': 60.0
        }
        
    def observe_behavior(self, observation: BehaviorObservation):
        """Record a behavior observation"""
        
        # Calculate risk score if not provided
        if observation.risk_score == 0.0:
            observation.risk_score = self._calculate_risk_score(observation)
        
        # Store observation
        self.observations.append(observation)
        self.behavior_sequences[observation.worker_id].append(observation)
        
        # Update worker profile
        self._update_worker_profile(observation)
        
        # Check for emerging patterns
        self._detect_patterns(observation.worker_id)
    
    def _calculate_risk_score(self, observation: BehaviorObservation) -> float:
        """Calculate risk score for a behavior (0-100)"""
        
        # Base scores by category
        category_scores = {
            BehaviorCategory.SAFE: 10,
            BehaviorCategory.AT_RISK: 40,
            BehaviorCategory.UNSAFE: 70,
            BehaviorCategory.VIOLATION: 90,
            BehaviorCategory.FATIGUE: 65,
            BehaviorCategory.DISTRACTED: 55,
            BehaviorCategory.RUSHING: 60,
            BehaviorCategory.COMPLACENT: 50
        }
        
        base_score = category_scores.get(observation.category, 50)
        
        # Adjust by confidence
        risk_score = base_score * observation.confidence
        
        # Context adjustments
        context = observation.context
        
        # High-risk location
        if context.get('high_risk_area'):
            risk_score *= 1.3
        
        # Operating machinery
        if context.get('operating_machinery'):
            risk_score *= 1.2
        
        # Working at height
        if context.get('working_at_height'):
            risk_score *= 1.4
        
        # Multiple violations
        if context.get('concurrent_violations', 0) > 1:
            risk_score *= (1 + 0.2 * context['concurrent_violations'])
        
        return min(100.0, risk_score)
    
    def _update_worker_profile(self, observation: BehaviorObservation):
        """Update worker behavioral profile"""
        
        worker_id = observation.worker_id
        
        # Initialize profile if new worker
        if worker_id not in self.worker_profiles:
            self.worker_profiles[worker_id] = WorkerProfile(
                worker_id=worker_id,
                name=observation.context.get('worker_name', f"Worker-{worker_id}"),
                observations_count=0,
                safe_behaviors=0,
                unsafe_behaviors=0,
                violations=0,
                average_risk_score=0.0,
                behavior_trends={},
                risk_patterns=[],
                strengths=[],
                areas_of_concern=[],
                last_updated=datetime.now()
            )
        
        profile = self.worker_profiles[worker_id]
        
        # Update counts
        profile.observations_count += 1
        
        if observation.category == BehaviorCategory.SAFE:
            profile.safe_behaviors += 1
        elif observation.category in [BehaviorCategory.UNSAFE, BehaviorCategory.AT_RISK]:
            profile.unsafe_behaviors += 1
        elif observation.category == BehaviorCategory.VIOLATION:
            profile.violations += 1
        
        # Update average risk score (moving average)
        alpha = 0.2  # Smoothing factor
        profile.average_risk_score = (
            alpha * observation.risk_score +
            (1 - alpha) * profile.average_risk_score
        )
        
        # Update behavior trends
        behavior_type = observation.behavior_type.value
        if behavior_type not in profile.behavior_trends:
            profile.behavior_trends[behavior_type] = 0.0
        
        profile.behavior_trends[behavior_type] = (
            alpha * observation.risk_score +
            (1 - alpha) * profile.behavior_trends[behavior_type]
        )
        
        profile.last_updated = datetime.now()
        
        # Analyze strengths and concerns
        self._analyze_worker_strengths_concerns(worker_id)
    
    def _analyze_worker_strengths_concerns(self, worker_id: str):
        """Analyze worker's strengths and areas of concern"""
        
        profile = self.worker_profiles[worker_id]
        
        # Get recent observations (last 7 days)
        cutoff = datetime.now() - timedelta(days=7)
        recent_obs = [
            obs for obs in self.behavior_sequences[worker_id]
            if obs.timestamp >= cutoff
        ]
        
        if not recent_obs:
            return
        
        # Analyze by behavior type
        behavior_stats = defaultdict(lambda: {'safe': 0, 'unsafe': 0})
        
        for obs in recent_obs:
            behavior_type = obs.behavior_type.value
            if obs.category == BehaviorCategory.SAFE:
                behavior_stats[behavior_type]['safe'] += 1
            else:
                behavior_stats[behavior_type]['unsafe'] += 1
        
        # Identify strengths (>80% safe)
        strengths = []
        for behavior_type, stats in behavior_stats.items():
            total = stats['safe'] + stats['unsafe']
            if total >= 3:  # Minimum observations
                safe_rate = stats['safe'] / total
                if safe_rate >= 0.8:
                    strengths.append(f"{behavior_type.replace('_', ' ').title()}")
        
        # Identify concerns (<60% safe)
        concerns = []
        for behavior_type, stats in behavior_stats.items():
            total = stats['safe'] + stats['unsafe']
            if total >= 3:
                safe_rate = stats['safe'] / total
                if safe_rate < 0.6:
                    concerns.append(f"{behavior_type.replace('_', ' ').title()}")
        
        profile.strengths = strengths
        profile.areas_of_concern = concerns
    
    def _detect_patterns(self, worker_id: str):
        """Detect behavioral patterns for a worker"""
        
        # Get recent observations
        cutoff = datetime.now() - timedelta(hours=self.pattern_thresholds['time_window_hours'])
        recent_obs = [
            obs for obs in self.behavior_sequences[worker_id]
            if obs.timestamp >= cutoff
        ]
        
        if len(recent_obs) < self.pattern_thresholds['minimum_occurrences']:
            return
        
        # Pattern 1: Repeated unsafe behavior
        unsafe_obs = [obs for obs in recent_obs if obs.category in [BehaviorCategory.UNSAFE, BehaviorCategory.VIOLATION]]
        if len(unsafe_obs) >= 3:
            # Check if same behavior type
            behavior_counter = Counter([obs.behavior_type for obs in unsafe_obs])
            for behavior_type, count in behavior_counter.items():
                if count >= 3:
                    self._create_pattern(
                        worker_id=worker_id,
                        pattern_type="repeated_unsafe_behavior",
                        description=f"Repeated unsafe {behavior_type.value.replace('_', ' ')}",
                        observations=unsafe_obs,
                        risk_level="high",
                        recommended_intervention=f"Immediate retraining on {behavior_type.value.replace('_', ' ')}"
                    )
        
        # Pattern 2: Degrading performance (increasing risk scores over time)
        if len(recent_obs) >= 5:
            time_sorted = sorted(recent_obs, key=lambda x: x.timestamp)
            risk_scores = [obs.risk_score for obs in time_sorted]
            
            # Simple trend detection
            first_half_avg = np.mean(risk_scores[:len(risk_scores)//2])
            second_half_avg = np.mean(risk_scores[len(risk_scores)//2:])
            
            if second_half_avg > first_half_avg * 1.3:  # 30% increase
                self._create_pattern(
                    worker_id=worker_id,
                    pattern_type="degrading_performance",
                    description="Risk scores increasing over time",
                    observations=recent_obs,
                    risk_level="moderate",
                    recommended_intervention="Check for fatigue, stress, or equipment issues"
                )
        
        # Pattern 3: Time-based patterns (e.g., end of shift fatigue)
        if len(recent_obs) >= 4:
            # Group by hour
            hour_risk = defaultdict(list)
            for obs in recent_obs:
                hour = obs.timestamp.hour
                hour_risk[hour].append(obs.risk_score)
            
            # Find high-risk hours
            for hour, scores in hour_risk.items():
                if len(scores) >= 2 and np.mean(scores) > 60:
                    self._create_pattern(
                        worker_id=worker_id,
                        pattern_type="time_based_risk",
                        description=f"Higher risk behaviors around hour {hour}:00",
                        observations=[obs for obs in recent_obs if obs.timestamp.hour == hour],
                        risk_level="moderate",
                        recommended_intervention=f"Implement additional breaks or supervision around {hour}:00"
                    )
        
        # Pattern 4: Rushing behavior sequence
        rushing_obs = [obs for obs in recent_obs if obs.category == BehaviorCategory.RUSHING]
        if len(rushing_obs) >= 3:
            self._create_pattern(
                worker_id=worker_id,
                pattern_type="rushing_behavior",
                description="Frequent rushing detected",
                observations=rushing_obs,
                risk_level="high",
                recommended_intervention="Review work load and time pressures"
            )
    
    def _create_pattern(
        self,
        worker_id: str,
        pattern_type: str,
        description: str,
        observations: List[BehaviorObservation],
        risk_level: str,
        recommended_intervention: str
    ):
        """Create a detected pattern"""
        
        # Check if pattern already exists
        existing = [
            p for p in self.patterns
            if p.worker_id == worker_id and p.pattern_type == pattern_type and p.risk_level == risk_level
        ]
        
        if existing:
            # Update existing pattern
            pattern = existing[0]
            pattern.frequency += len(observations)
            pattern.last_seen = max([obs.timestamp for obs in observations])
        else:
            # Create new pattern
            pattern = BehaviorPattern(
                pattern_id=f"PAT-{len(self.patterns) + 1:06d}",
                worker_id=worker_id,
                pattern_type=pattern_type,
                description=description,
                frequency=len(observations),
                first_seen=min([obs.timestamp for obs in observations]),
                last_seen=max([obs.timestamp for obs in observations]),
                risk_level=risk_level,
                predictive_indicators=self._extract_predictive_indicators(observations),
                recommended_intervention=recommended_intervention,
                confidence=min(1.0, len(observations) / 10.0)  # More observations = higher confidence
            )
            
            self.patterns.append(pattern)
            
            # Update worker profile
            if worker_id in self.worker_profiles:
                if pattern.pattern_type not in self.worker_profiles[worker_id].risk_patterns:
                    self.worker_profiles[worker_id].risk_patterns.append(pattern.pattern_type)
    
    def _extract_predictive_indicators(self, observations: List[BehaviorObservation]) -> List[str]:
        """Extract predictive indicators from observations"""
        
        indicators = []
        
        # Common behavior types
        behavior_counter = Counter([obs.behavior_type.value for obs in observations])
        most_common = behavior_counter.most_common(2)
        indicators.extend([f"{bt.replace('_', ' ').title()}" for bt, _ in most_common])
        
        # Common contexts
        contexts = [obs.context for obs in observations]
        
        # High risk areas
        if any(ctx.get('high_risk_area') for ctx in contexts):
            indicators.append("Often in high-risk areas")
        
        # Time patterns
        hours = [obs.timestamp.hour for obs in observations]
        hour_counter = Counter(hours)
        common_hours = [h for h, count in hour_counter.items() if count >= 2]
        if common_hours:
            indicators.append(f"Frequent around {common_hours[0]}:00")
        
        return indicators[:5]  # Top 5 indicators
    
    def predict_next_risk(self, worker_id: str) -> Dict[str, Any]:
        """Predict next potential risk for a worker"""
        
        if worker_id not in self.worker_profiles:
            return {
                'risk_probability': 0.0,
                'predicted_behavior': 'unknown',
                'confidence': 0.0,
                'recommendation': 'Insufficient data'
            }
        
        profile = self.worker_profiles[worker_id]
        recent_obs = self.behavior_sequences[worker_id][-10:]  # Last 10 observations
        
        if len(recent_obs) < 3:
            return {
                'risk_probability': profile.average_risk_score / 100.0,
                'predicted_behavior': 'insufficient_data',
                'confidence': 0.3,
                'recommendation': 'Continue monitoring'
            }
        
        # Analyze recent trend
        recent_risks = [obs.risk_score for obs in recent_obs]
        trend = np.polyfit(range(len(recent_risks)), recent_risks, 1)[0]  # Linear slope
        
        # Predict next risk score
        predicted_risk = recent_risks[-1] + trend
        predicted_risk = max(0.0, min(100.0, predicted_risk))
        
        # Identify most likely unsafe behavior
        recent_types = [obs.behavior_type for obs in recent_obs if obs.risk_score > 50]
        most_likely_behavior = Counter(recent_types).most_common(1)[0][0].value if recent_types else "unknown"
        
        # Confidence based on data quality
        confidence = min(1.0, len(recent_obs) / 10.0) * (1.0 - abs(trend) / 50.0)
        
        # Generate recommendation
        if predicted_risk > 70:
            recommendation = f"High risk predicted. Immediate intervention needed for {most_likely_behavior.replace('_', ' ')}"
        elif predicted_risk > 50:
            recommendation = f"Moderate risk. Enhanced monitoring and coaching on {most_likely_behavior.replace('_', ' ')}"
        else:
            recommendation = "Low risk. Continue standard monitoring"
        
        return {
            'risk_probability': predicted_risk / 100.0,
            'predicted_behavior': most_likely_behavior,
            'trend': 'increasing' if trend > 0 else 'decreasing',
            'confidence': confidence,
            'recommendation': recommendation,
            'contributing_patterns': [p.pattern_type for p in self.patterns if p.worker_id == worker_id]
        }
    
    def get_team_risk_analysis(self, team_ids: List[str]) -> Dict[str, Any]:
        """Analyze risk across a team"""
        
        team_profiles = [
            self.worker_profiles[wid] for wid in team_ids
            if wid in self.worker_profiles
        ]
        
        if not team_profiles:
            return {
                'team_average_risk': 0.0,
                'high_risk_workers': [],
                'team_strengths': [],
                'team_concerns': []
            }
        
        # Calculate team average risk
        team_avg_risk = np.mean([p.average_risk_score for p in team_profiles])
        
        # Identify high-risk workers (>60)
        high_risk = [
            {
                'worker_id': p.worker_id,
                'name': p.name,
                'risk_score': p.average_risk_score,
                'patterns': p.risk_patterns
            }
            for p in team_profiles
            if p.average_risk_score > 60
        ]
        
        # Team-wide strengths
        all_strengths = []
        for p in team_profiles:
            all_strengths.extend(p.strengths)
        team_strengths = [s for s, count in Counter(all_strengths).most_common(5)]
        
        # Team-wide concerns
        all_concerns = []
        for p in team_profiles:
            all_concerns.extend(p.areas_of_concern)
        team_concerns = [c for c, count in Counter(all_concerns).most_common(5)]
        
        return {
            'team_size': len(team_profiles),
            'team_average_risk': team_avg_risk,
            'high_risk_workers': high_risk,
            'team_strengths': team_strengths,
            'team_concerns': team_concerns,
            'recommendation': self._generate_team_recommendation(team_avg_risk, high_risk, team_concerns)
        }
    
    def _generate_team_recommendation(
        self,
        team_avg_risk: float,
        high_risk_workers: List[Dict],
        team_concerns: List[str]
    ) -> str:
        """Generate team-level recommendation"""
        
        if team_avg_risk > 60:
            return f"URGENT: Team at high risk (avg: {team_avg_risk:.1f}). Immediate team-wide safety review required."
        elif len(high_risk_workers) >= 3:
            return f"Multiple high-risk workers detected ({len(high_risk_workers)}). Focus on individual interventions."
        elif team_concerns:
            top_concern = team_concerns[0]
            return f"Team-wide improvement needed in: {top_concern}. Consider targeted training program."
        else:
            return "Team performing well. Maintain current safety practices."


# Global behavioral pattern recognition instance
behavioral_recognition = BehavioralPatternRecognition()
