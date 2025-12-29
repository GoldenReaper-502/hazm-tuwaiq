"""
HAZM TUWAIQ - Advanced Fatigue Detection (Enhanced)
Multi-factor fatigue detection using physiological, behavioral, and environmental signals
Prevents accidents through early fatigue intervention
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, time
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
import numpy as np


class FatigueLevel(str, Enum):
    """Fatigue severity levels"""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"
    CRITICAL = "critical"


class FatigueIndicator(str, Enum):
    """Types of fatigue indicators"""
    EYE_CLOSURE = "eye_closure"  # PERCLOS - Percentage of eye closure
    BLINK_RATE = "blink_rate"
    YAWNING = "yawning"
    HEAD_NODDING = "head_nodding"
    REACTION_TIME = "reaction_time"
    MOVEMENT_SPEED = "movement_speed"
    ERROR_RATE = "error_rate"
    WORK_PACE = "work_pace"
    HEART_RATE_VARIABILITY = "heart_rate_variability"
    BODY_TEMPERATURE = "body_temperature"


@dataclass
class FatigueSignal:
    """Individual fatigue signal"""
    worker_id: str
    timestamp: datetime
    indicator_type: FatigueIndicator
    value: float
    severity: float  # 0-1
    

@dataclass
class FatigueAssessment:
    """Comprehensive fatigue assessment"""
    worker_id: str
    assessment_time: datetime
    fatigue_level: FatigueLevel
    fatigue_score: float  # 0-100
    confidence: float  # 0-1
    contributing_factors: List[Dict[str, Any]]
    physiological_score: float
    behavioral_score: float
    environmental_score: float
    work_duration_hours: float
    time_since_break: float  # minutes
    recommended_actions: List[str]
    risk_of_accident: float  # 0-1
    

@dataclass
class WorkShift:
    """Worker shift information"""
    worker_id: str
    shift_start: datetime
    shift_end: Optional[datetime]
    breaks_taken: List[datetime]
    total_break_minutes: float
    

class AdvancedFatigueDetection:
    """
    Advanced multi-modal fatigue detection system
    
    Features:
    - Multi-factor fatigue assessment (physiological + behavioral + environmental)
    - Circadian rhythm consideration
    - Work duration and break pattern analysis
    - Individual baseline adaptation
    - Early warning system
    - Personalized intervention recommendations
    """
    
    def __init__(self):
        self.fatigue_signals: List[FatigueSignal] = []
        self.fatigue_assessments: List[FatigueAssessment] = []
        self.work_shifts: Dict[str, WorkShift] = {}
        self.worker_baselines: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # Fatigue indicator weights
        self.indicator_weights = {
            FatigueIndicator.EYE_CLOSURE: 0.20,  # PERCLOS is highly reliable
            FatigueIndicator.BLINK_RATE: 0.10,
            FatigueIndicator.YAWNING: 0.15,
            FatigueIndicator.HEAD_NODDING: 0.12,
            FatigueIndicator.REACTION_TIME: 0.15,
            FatigueIndicator.MOVEMENT_SPEED: 0.08,
            FatigueIndicator.ERROR_RATE: 0.10,
            FatigueIndicator.WORK_PACE: 0.05,
            FatigueIndicator.HEART_RATE_VARIABILITY: 0.03,
            FatigueIndicator.BODY_TEMPERATURE: 0.02
        }
        
        # Circadian rhythm factors (hour of day -> fatigue multiplier)
        self.circadian_multipliers = {
            0: 1.5, 1: 1.6, 2: 1.7, 3: 1.8,  # Night hours - high fatigue
            4: 1.6, 5: 1.4, 6: 1.2, 7: 1.0,
            8: 0.9, 9: 0.8, 10: 0.8, 11: 0.9,  # Morning - low fatigue
            12: 1.0, 13: 1.1, 14: 1.3, 15: 1.2,  # Post-lunch dip
            16: 1.0, 17: 0.9, 18: 1.0, 19: 1.1,
            20: 1.2, 21: 1.3, 22: 1.4, 23: 1.5   # Evening - increasing fatigue
        }
    
    def start_shift(
        self,
        worker_id: str,
        shift_start: datetime,
        shift_end: Optional[datetime] = None
    ):
        """Record shift start"""
        
        self.work_shifts[worker_id] = WorkShift(
            worker_id=worker_id,
            shift_start=shift_start,
            shift_end=shift_end,
            breaks_taken=[],
            total_break_minutes=0.0
        )
    
    def record_break(self, worker_id: str, break_duration_minutes: float):
        """Record a worker break"""
        
        if worker_id in self.work_shifts:
            self.work_shifts[worker_id].breaks_taken.append(datetime.now())
            self.work_shifts[worker_id].total_break_minutes += break_duration_minutes
    
    def ingest_fatigue_signal(self, signal: FatigueSignal):
        """Ingest a fatigue indicator signal"""
        
        self.fatigue_signals.append(signal)
        
        # Update worker baseline if this is normal behavior
        if signal.severity < 0.3:  # Low severity = normal baseline
            self._update_baseline(signal)
    
    def _update_baseline(self, signal: FatigueSignal):
        """Update worker's baseline for this indicator"""
        
        worker_id = signal.worker_id
        indicator = signal.indicator_type.value
        
        # Moving average
        alpha = 0.1  # Slow adaptation
        
        if indicator in self.worker_baselines[worker_id]:
            self.worker_baselines[worker_id][indicator] = (
                alpha * signal.value +
                (1 - alpha) * self.worker_baselines[worker_id][indicator]
            )
        else:
            self.worker_baselines[worker_id][indicator] = signal.value
    
    def assess_fatigue(self, worker_id: str) -> FatigueAssessment:
        """
        Comprehensive fatigue assessment for a worker
        
        Returns complete fatigue analysis with recommendations
        """
        
        now = datetime.now()
        
        # Get recent signals (last 5 minutes)
        recent_signals = [
            s for s in self.fatigue_signals
            if s.worker_id == worker_id and (now - s.timestamp).total_seconds() <= 300
        ]
        
        # Calculate physiological score
        physiological_score = self._calculate_physiological_score(recent_signals)
        
        # Calculate behavioral score
        behavioral_score = self._calculate_behavioral_score(recent_signals)
        
        # Calculate environmental score (work duration, breaks, time of day)
        environmental_score = self._calculate_environmental_score(worker_id, now)
        
        # Combined fatigue score (0-100)
        fatigue_score = (
            physiological_score * 0.5 +
            behavioral_score * 0.3 +
            environmental_score * 0.2
        )
        
        # Apply circadian rhythm multiplier
        hour = now.hour
        circadian_multiplier = self.circadian_multipliers.get(hour, 1.0)
        fatigue_score *= circadian_multiplier
        
        fatigue_score = min(100.0, fatigue_score)
        
        # Determine fatigue level
        fatigue_level = self._get_fatigue_level(fatigue_score)
        
        # Identify contributing factors
        contributing_factors = self._identify_contributing_factors(
            recent_signals,
            worker_id,
            now
        )
        
        # Calculate confidence
        confidence = min(1.0, len(recent_signals) / 10.0)  # More signals = higher confidence
        
        # Calculate risk of accident
        risk_of_accident = self._calculate_accident_risk(fatigue_score, fatigue_level)
        
        # Generate recommendations
        recommended_actions = self._generate_fatigue_recommendations(
            fatigue_level,
            contributing_factors,
            worker_id
        )
        
        # Work duration
        work_duration = self._get_work_duration(worker_id)
        time_since_break = self._get_time_since_last_break(worker_id)
        
        assessment = FatigueAssessment(
            worker_id=worker_id,
            assessment_time=now,
            fatigue_level=fatigue_level,
            fatigue_score=fatigue_score,
            confidence=confidence,
            contributing_factors=contributing_factors,
            physiological_score=physiological_score,
            behavioral_score=behavioral_score,
            environmental_score=environmental_score,
            work_duration_hours=work_duration,
            time_since_break=time_since_break,
            recommended_actions=recommended_actions,
            risk_of_accident=risk_of_accident
        )
        
        self.fatigue_assessments.append(assessment)
        
        return assessment
    
    def _calculate_physiological_score(self, signals: List[FatigueSignal]) -> float:
        """Calculate physiological fatigue score"""
        
        physiological_indicators = [
            FatigueIndicator.EYE_CLOSURE,
            FatigueIndicator.BLINK_RATE,
            FatigueIndicator.YAWNING,
            FatigueIndicator.HEAD_NODDING,
            FatigueIndicator.HEART_RATE_VARIABILITY,
            FatigueIndicator.BODY_TEMPERATURE
        ]
        
        relevant_signals = [s for s in signals if s.indicator_type in physiological_indicators]
        
        if not relevant_signals:
            return 0.0
        
        # Weighted average of severities
        total_weight = 0.0
        weighted_sum = 0.0
        
        for signal in relevant_signals:
            weight = self.indicator_weights.get(signal.indicator_type, 0.1)
            weighted_sum += signal.severity * weight * 100.0
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _calculate_behavioral_score(self, signals: List[FatigueSignal]) -> float:
        """Calculate behavioral fatigue score"""
        
        behavioral_indicators = [
            FatigueIndicator.REACTION_TIME,
            FatigueIndicator.MOVEMENT_SPEED,
            FatigueIndicator.ERROR_RATE,
            FatigueIndicator.WORK_PACE
        ]
        
        relevant_signals = [s for s in signals if s.indicator_type in behavioral_indicators]
        
        if not relevant_signals:
            return 0.0
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for signal in relevant_signals:
            weight = self.indicator_weights.get(signal.indicator_type, 0.1)
            weighted_sum += signal.severity * weight * 100.0
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _calculate_environmental_score(self, worker_id: str, now: datetime) -> float:
        """Calculate environmental/contextual fatigue score"""
        
        score = 0.0
        
        # Work duration factor
        work_duration = self._get_work_duration(worker_id)
        if work_duration > 4.0:  # More than 4 hours
            score += (work_duration - 4.0) * 10.0  # 10 points per hour over 4
        
        # Time since break factor
        time_since_break = self._get_time_since_last_break(worker_id)
        if time_since_break > 120:  # More than 2 hours
            score += (time_since_break - 120) / 10.0
        
        # Night shift factor
        hour = now.hour
        if 0 <= hour <= 6:  # Night hours
            score += 20.0
        
        return min(100.0, score)
    
    def _get_work_duration(self, worker_id: str) -> float:
        """Get hours worked in current shift"""
        
        if worker_id not in self.work_shifts:
            return 0.0
        
        shift = self.work_shifts[worker_id]
        duration = (datetime.now() - shift.shift_start).total_seconds() / 3600.0
        
        # Subtract break time
        duration -= shift.total_break_minutes / 60.0
        
        return max(0.0, duration)
    
    def _get_time_since_last_break(self, worker_id: str) -> float:
        """Get minutes since last break"""
        
        if worker_id not in self.work_shifts or not self.work_shifts[worker_id].breaks_taken:
            # No breaks, time since shift start
            if worker_id in self.work_shifts:
                return (datetime.now() - self.work_shifts[worker_id].shift_start).total_seconds() / 60.0
            return 0.0
        
        last_break = self.work_shifts[worker_id].breaks_taken[-1]
        return (datetime.now() - last_break).total_seconds() / 60.0
    
    def _get_fatigue_level(self, fatigue_score: float) -> FatigueLevel:
        """Convert fatigue score to level"""
        
        if fatigue_score >= 85:
            return FatigueLevel.CRITICAL
        elif fatigue_score >= 70:
            return FatigueLevel.SEVERE
        elif fatigue_score >= 55:
            return FatigueLevel.HIGH
        elif fatigue_score >= 35:
            return FatigueLevel.MODERATE
        elif fatigue_score >= 15:
            return FatigueLevel.LOW
        else:
            return FatigueLevel.NONE
    
    def _identify_contributing_factors(
        self,
        signals: List[FatigueSignal],
        worker_id: str,
        now: datetime
    ) -> List[Dict[str, Any]]:
        """Identify main contributing factors to fatigue"""
        
        factors = []
        
        # High severity signals
        high_severity = [s for s in signals if s.severity > 0.6]
        for signal in high_severity:
            factors.append({
                'factor': signal.indicator_type.value,
                'severity': signal.severity,
                'category': 'physiological' if signal.indicator_type in [
                    FatigueIndicator.EYE_CLOSURE,
                    FatigueIndicator.YAWNING,
                    FatigueIndicator.HEAD_NODDING
                ] else 'behavioral'
            })
        
        # Work duration
        work_duration = self._get_work_duration(worker_id)
        if work_duration > 6.0:
            factors.append({
                'factor': 'extended_work_duration',
                'severity': min(1.0, (work_duration - 6.0) / 4.0),
                'category': 'environmental',
                'value': f"{work_duration:.1f} hours"
            })
        
        # No breaks
        time_since_break = self._get_time_since_last_break(worker_id)
        if time_since_break > 180:  # 3 hours
            factors.append({
                'factor': 'inadequate_breaks',
                'severity': min(1.0, (time_since_break - 180) / 120.0),
                'category': 'environmental',
                'value': f"{time_since_break:.0f} minutes since break"
            })
        
        # Time of day
        hour = now.hour
        if 0 <= hour <= 6 or 14 <= hour <= 16:  # Night or post-lunch dip
            factors.append({
                'factor': 'circadian_low_point',
                'severity': 0.7 if 0 <= hour <= 6 else 0.4,
                'category': 'circadian',
                'value': f"Hour {hour}"
            })
        
        # Sort by severity
        factors.sort(key=lambda f: f['severity'], reverse=True)
        
        return factors[:5]  # Top 5
    
    def _calculate_accident_risk(self, fatigue_score: float, fatigue_level: FatigueLevel) -> float:
        """Calculate risk of accident due to fatigue"""
        
        # Base risk from fatigue score
        base_risk = fatigue_score / 100.0
        
        # Exponential increase at high fatigue
        if fatigue_level in [FatigueLevel.SEVERE, FatigueLevel.CRITICAL]:
            base_risk = base_risk ** 0.7  # Accelerated risk growth
        
        # Studies show fatigue doubles accident risk at moderate levels, 4x at high
        risk_multipliers = {
            FatigueLevel.NONE: 1.0,
            FatigueLevel.LOW: 1.2,
            FatigueLevel.MODERATE: 2.0,
            FatigueLevel.HIGH: 3.0,
            FatigueLevel.SEVERE: 5.0,
            FatigueLevel.CRITICAL: 8.0
        }
        
        multiplier = risk_multipliers.get(fatigue_level, 1.0)
        
        return min(1.0, base_risk * multiplier)
    
    def _generate_fatigue_recommendations(
        self,
        fatigue_level: FatigueLevel,
        contributing_factors: List[Dict[str, Any]],
        worker_id: str
    ) -> List[str]:
        """Generate intervention recommendations"""
        
        recommendations = []
        
        # Urgency-based recommendations
        if fatigue_level == FatigueLevel.CRITICAL:
            recommendations.append("CRITICAL: Remove worker from duty immediately")
            recommendations.append("Provide immediate rest period (minimum 30 minutes)")
            recommendations.append("Evaluate if worker is fit to continue shift")
        elif fatigue_level == FatigueLevel.SEVERE:
            recommendations.append("URGENT: Mandatory break required (20-30 minutes)")
            recommendations.append("Assign to low-risk tasks only after break")
            recommendations.append("Consider early shift end")
        elif fatigue_level == FatigueLevel.HIGH:
            recommendations.append("Schedule break within next 15 minutes")
            recommendations.append("Reduce task complexity and workload")
            recommendations.append("Increase supervision")
        elif fatigue_level == FatigueLevel.MODERATE:
            recommendations.append("Recommend break in next 30 minutes")
            recommendations.append("Monitor closely for increasing fatigue")
        else:
            recommendations.append("Continue normal monitoring")
        
        # Factor-specific recommendations
        for factor in contributing_factors[:3]:  # Top 3 factors
            if factor['factor'] == 'extended_work_duration':
                recommendations.append("Schedule additional rest breaks")
            elif factor['factor'] == 'inadequate_breaks':
                recommendations.append("Enforce mandatory break policy")
            elif factor['factor'] == 'circadian_low_point':
                recommendations.append("Consider task rotation during circadian low periods")
            elif 'eye_closure' in factor['factor']:
                recommendations.append("Provide visual rest breaks")
        
        return list(set(recommendations))[:6]  # Unique, top 6
    
    def get_team_fatigue_report(self, worker_ids: List[str]) -> Dict[str, Any]:
        """Get fatigue report for a team"""
        
        assessments = [self.assess_fatigue(wid) for wid in worker_ids]
        
        if not assessments:
            return {
                'team_size': 0,
                'average_fatigue': 0.0,
                'critical_count': 0
            }
        
        # Calculate team statistics
        fatigue_scores = [a.fatigue_score for a in assessments]
        avg_fatigue = np.mean(fatigue_scores)
        max_fatigue = np.max(fatigue_scores)
        
        # Count by level
        level_counts = defaultdict(int)
        for assessment in assessments:
            level_counts[assessment.fatigue_level.value] += 1
        
        # High-risk workers
        high_risk = [
            {
                'worker_id': a.worker_id,
                'fatigue_score': a.fatigue_score,
                'fatigue_level': a.fatigue_level.value,
                'accident_risk': a.risk_of_accident,
                'recommendations': a.recommended_actions
            }
            for a in assessments
            if a.fatigue_level in [FatigueLevel.HIGH, FatigueLevel.SEVERE, FatigueLevel.CRITICAL]
        ]
        
        return {
            'team_size': len(assessments),
            'average_fatigue': avg_fatigue,
            'max_fatigue': max_fatigue,
            'fatigue_distribution': dict(level_counts),
            'critical_count': level_counts[FatigueLevel.CRITICAL.value],
            'severe_count': level_counts[FatigueLevel.SEVERE.value],
            'high_risk_workers': high_risk,
            'team_recommendation': self._generate_team_recommendation(avg_fatigue, high_risk)
        }
    
    def _generate_team_recommendation(
        self,
        avg_fatigue: float,
        high_risk_workers: List[Dict]
    ) -> str:
        """Generate team-level recommendation"""
        
        if len(high_risk_workers) >= 3 or avg_fatigue > 60:
            return "TEAM ALERT: Multiple workers showing high fatigue. Consider team break or shift rotation."
        elif high_risk_workers:
            return f"Individual interventions needed for {len(high_risk_workers)} worker(s)."
        elif avg_fatigue > 40:
            return "Team fatigue levels moderate. Ensure break schedules are maintained."
        else:
            return "Team fatigue levels normal. Continue standard monitoring."


# Global advanced fatigue detection instance
advanced_fatigue_detection = AdvancedFatigueDetection()
