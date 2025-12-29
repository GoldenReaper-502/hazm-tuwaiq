"""
HAZM TUWAIQ - Intelligent Compliance Drift Detection
Detects gradual deviations from safety standards before they become violations
Prevents normalization of deviance
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, deque
import numpy as np


class ComplianceCategory(str, Enum):
    """Categories of compliance"""
    PPE = "ppe"
    PROCEDURES = "procedures"
    PERMITS = "permits"
    TRAINING = "training"
    EQUIPMENT_INSPECTION = "equipment_inspection"
    HOUSEKEEPING = "housekeeping"
    DOCUMENTATION = "documentation"
    ENVIRONMENTAL = "environmental"


class DriftSeverity(str, Enum):
    """Severity of compliance drift"""
    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    SEVERE = "severe"


@dataclass
class ComplianceObservation:
    """Single compliance observation"""
    observation_id: str
    timestamp: datetime
    category: ComplianceCategory
    requirement: str
    actual_compliance: float  # 0-1 (0 = non-compliant, 1 = fully compliant)
    location: str
    worker_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    

@dataclass
class ComplianceDrift:
    """Detected compliance drift"""
    drift_id: str
    category: ComplianceCategory
    requirement: str
    detected_at: datetime
    drift_start_date: datetime
    baseline_compliance: float  # Original compliance level
    current_compliance: float  # Current compliance level
    drift_magnitude: float  # How much drifted (0-1)
    drift_rate: float  # Rate of drift (per day)
    severity: DriftSeverity
    affected_areas: List[str]
    affected_workers: List[str]
    root_causes: List[str]
    recommended_interventions: List[str]
    confidence: float
    

@dataclass
class ComplianceBaseline:
    """Baseline compliance level"""
    category: ComplianceCategory
    requirement: str
    baseline_level: float  # 0-1
    established_date: datetime
    observation_count: int
    standard_deviation: float
    

class IntelligentComplianceDrift:
    """
    Intelligent compliance drift detection system
    
    Features:
    - Detects gradual deviations from compliance baselines
    - Identifies normalization of deviance patterns
    - Multi-factor drift analysis (time, location, personnel)
    - Early intervention recommendations
    - Root cause identification
    """
    
    def __init__(self):
        self.observations: List[ComplianceObservation] = []
        self.baselines: Dict[str, ComplianceBaseline] = {}
        self.detected_drifts: List[ComplianceDrift] = []
        
        # Rolling windows for drift detection
        self.observation_windows: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Drift detection thresholds
        self.drift_thresholds = {
            'minor_drift': 0.05,  # 5% deviation
            'moderate_drift': 0.10,
            'significant_drift': 0.20,
            'severe_drift': 0.30
        }
        
        # Minimum observations before establishing baseline
        self.min_baseline_observations = 20
    
    def record_observation(self, observation: ComplianceObservation):
        """Record a compliance observation"""
        
        self.observations.append(observation)
        
        # Add to rolling window
        key = f"{observation.category.value}:{observation.requirement}"
        self.observation_windows[key].append(observation)
        
        # Establish or update baseline
        self._update_baseline(observation)
        
        # Check for drift
        self._detect_drift(observation)
    
    def _update_baseline(self, observation: ComplianceObservation):
        """Establish or update compliance baseline"""
        
        key = f"{observation.category.value}:{observation.requirement}"
        window = self.observation_windows[key]
        
        # Need minimum observations to establish baseline
        if len(window) < self.min_baseline_observations:
            return
        
        # Calculate baseline from first observations
        if key not in self.baselines:
            first_observations = list(window)[:self.min_baseline_observations]
            compliance_levels = [obs.actual_compliance for obs in first_observations]
            
            self.baselines[key] = ComplianceBaseline(
                category=observation.category,
                requirement=observation.requirement,
                baseline_level=np.mean(compliance_levels),
                established_date=first_observations[0].timestamp,
                observation_count=len(first_observations),
                standard_deviation=np.std(compliance_levels)
            )
    
    def _detect_drift(self, observation: ComplianceObservation):
        """Detect compliance drift"""
        
        key = f"{observation.category.value}:{observation.requirement}"
        
        # Need baseline to detect drift
        if key not in self.baselines:
            return
        
        baseline = self.baselines[key]
        window = self.observation_windows[key]
        
        # Calculate recent compliance (last 20 observations)
        recent_obs = list(window)[-20:]
        recent_compliance = np.mean([obs.actual_compliance for obs in recent_obs])
        
        # Calculate drift
        drift_magnitude = baseline.baseline_level - recent_compliance
        
        # Only consider negative drift (deteriorating compliance)
        if drift_magnitude < self.drift_thresholds['minor_drift']:
            return
        
        # Determine severity
        severity = self._determine_drift_severity(drift_magnitude)
        
        # Calculate drift rate (change per day)
        if len(recent_obs) >= 2:
            time_span_days = (recent_obs[-1].timestamp - recent_obs[0].timestamp).days
            if time_span_days > 0:
                drift_rate = drift_magnitude / time_span_days
            else:
                drift_rate = 0.0
        else:
            drift_rate = 0.0
        
        # Estimate when drift started
        drift_start = self._estimate_drift_start(window, baseline.baseline_level)
        
        # Identify affected areas and workers
        affected_areas = list(set([obs.location for obs in recent_obs]))
        affected_workers = list(set([
            obs.worker_id for obs in recent_obs
            if obs.worker_id
        ]))
        
        # Identify root causes
        root_causes = self._identify_root_causes(recent_obs, baseline)
        
        # Generate intervention recommendations
        interventions = self._generate_interventions(
            observation.category,
            drift_magnitude,
            severity,
            root_causes
        )
        
        # Calculate confidence
        confidence = self._calculate_drift_confidence(window, baseline)
        
        # Check if this drift already detected
        existing_drift = next(
            (d for d in self.detected_drifts
             if d.category == observation.category and
             d.requirement == observation.requirement and
             d.severity == severity),
            None
        )
        
        if existing_drift:
            # Update existing drift
            existing_drift.current_compliance = recent_compliance
            existing_drift.drift_magnitude = drift_magnitude
            existing_drift.drift_rate = drift_rate
            existing_drift.affected_areas = affected_areas
            existing_drift.affected_workers = affected_workers
            existing_drift.confidence = confidence
        else:
            # Create new drift detection
            drift = ComplianceDrift(
                drift_id=f"DRIFT-{len(self.detected_drifts) + 1:06d}",
                category=observation.category,
                requirement=observation.requirement,
                detected_at=datetime.now(),
                drift_start_date=drift_start,
                baseline_compliance=baseline.baseline_level,
                current_compliance=recent_compliance,
                drift_magnitude=drift_magnitude,
                drift_rate=drift_rate,
                severity=severity,
                affected_areas=affected_areas,
                affected_workers=affected_workers,
                root_causes=root_causes,
                recommended_interventions=interventions,
                confidence=confidence
            )
            
            self.detected_drifts.append(drift)
    
    def _determine_drift_severity(self, drift_magnitude: float) -> DriftSeverity:
        """Determine drift severity"""
        
        if drift_magnitude >= self.drift_thresholds['severe_drift']:
            return DriftSeverity.SEVERE
        elif drift_magnitude >= self.drift_thresholds['significant_drift']:
            return DriftSeverity.SIGNIFICANT
        elif drift_magnitude >= self.drift_thresholds['moderate_drift']:
            return DriftSeverity.MODERATE
        elif drift_magnitude >= self.drift_thresholds['minor_drift']:
            return DriftSeverity.MINOR
        else:
            return DriftSeverity.NONE
    
    def _estimate_drift_start(
        self,
        window: deque,
        baseline_level: float
    ) -> datetime:
        """Estimate when drift started"""
        
        observations = list(window)
        
        # Find first observation significantly below baseline
        threshold = baseline_level - self.drift_thresholds['minor_drift']
        
        for obs in observations:
            if obs.actual_compliance < threshold:
                return obs.timestamp
        
        # Default to middle of window
        if observations:
            mid_index = len(observations) // 2
            return observations[mid_index].timestamp
        
        return datetime.now()
    
    def _identify_root_causes(
        self,
        recent_obs: List[ComplianceObservation],
        baseline: ComplianceBaseline
    ) -> List[str]:
        """Identify potential root causes of drift"""
        
        root_causes = []
        
        # Temporal patterns
        times_of_day = [obs.timestamp.hour for obs in recent_obs]
        if times_of_day:
            most_common_hour = max(set(times_of_day), key=times_of_day.count)
            if times_of_day.count(most_common_hour) / len(times_of_day) > 0.6:
                root_causes.append(f"Drift concentrated around hour {most_common_hour}:00 (shift fatigue or supervision gap)")
        
        # Location patterns
        locations = [obs.location for obs in recent_obs]
        if locations:
            most_common_location = max(set(locations), key=locations.count)
            if locations.count(most_common_location) / len(locations) > 0.5:
                root_causes.append(f"Drift concentrated in {most_common_location} (local culture issue)")
        
        # Worker patterns
        workers = [obs.worker_id for obs in recent_obs if obs.worker_id]
        if workers:
            unique_workers = len(set(workers))
            if unique_workers < len(workers) * 0.3:  # Same workers repeatedly
                root_causes.append("Drift involves small group of repeat offenders (targeted training needed)")
        
        # Gradual vs sudden drift
        compliance_levels = [obs.actual_compliance for obs in recent_obs]
        if len(compliance_levels) >= 3:
            # Check if drift is gradual (linear trend) or sudden (step change)
            trend = np.polyfit(range(len(compliance_levels)), compliance_levels, 1)[0]
            
            if abs(trend) > 0.01:  # Significant slope
                root_causes.append("Gradual drift pattern (normalization of deviance - systemic issue)")
            else:
                root_causes.append("Sudden drift pattern (recent policy change or leadership change)")
        
        # Category-specific root causes
        if baseline.category == ComplianceCategory.PPE:
            root_causes.append("Possible PPE availability or comfort issues")
        elif baseline.category == ComplianceCategory.PROCEDURES:
            root_causes.append("Procedures may be outdated or impractical")
        elif baseline.category == ComplianceCategory.TRAINING:
            root_causes.append("Training refresh needed")
        
        return root_causes[:5]  # Top 5
    
    def _generate_interventions(
        self,
        category: ComplianceCategory,
        drift_magnitude: float,
        severity: DriftSeverity,
        root_causes: List[str]
    ) -> List[str]:
        """Generate intervention recommendations"""
        
        interventions = []
        
        # Urgency-based interventions
        if severity in [DriftSeverity.SEVERE, DriftSeverity.SIGNIFICANT]:
            interventions.append("URGENT: Immediate leadership intervention required")
            interventions.append("Conduct site-wide safety stand-down")
            interventions.append("Reset compliance expectations with clear consequences")
        elif severity == DriftSeverity.MODERATE:
            interventions.append("Schedule compliance reinforcement training within 48 hours")
            interventions.append("Increase supervisory oversight")
        else:
            interventions.append("Provide gentle compliance reminders")
            interventions.append("Review with team leads")
        
        # Root cause-based interventions
        for cause in root_causes:
            if "shift fatigue" in cause.lower():
                interventions.append("Review shift schedules and break patterns")
            elif "local culture" in cause.lower():
                interventions.append("Deploy safety champion to affected area")
            elif "repeat offenders" in cause.lower():
                interventions.append("Implement one-on-one coaching for repeat offenders")
            elif "normalization" in cause.lower():
                interventions.append("Reset safety culture with visible leadership commitment")
            elif "policy change" in cause.lower():
                interventions.append("Clarify recent policy changes and rationale")
        
        # Category-specific interventions
        if category == ComplianceCategory.PPE:
            interventions.append("Audit PPE availability and fit")
            interventions.append("Review PPE comfort and suitability for task")
        elif category == ComplianceCategory.PROCEDURES:
            interventions.append("Review procedure practicality with frontline workers")
            interventions.append("Update procedures if necessary")
        elif category == ComplianceCategory.TRAINING:
            interventions.append("Schedule refresher training sessions")
        
        return list(set(interventions))[:8]  # Unique, top 8
    
    def _calculate_drift_confidence(
        self,
        window: deque,
        baseline: ComplianceBaseline
    ) -> float:
        """Calculate confidence in drift detection"""
        
        # More observations = higher confidence
        observation_factor = min(1.0, len(window) / 50.0)
        
        # Lower baseline variance = higher confidence
        if baseline.standard_deviation > 0:
            variance_factor = 1.0 / (1.0 + baseline.standard_deviation)
        else:
            variance_factor = 1.0
        
        # Consistent drift direction = higher confidence
        recent_obs = list(window)[-20:]
        if len(recent_obs) >= 5:
            compliance_levels = [obs.actual_compliance for obs in recent_obs]
            # Check monotonicity
            decreasing_count = sum(
                1 for i in range(1, len(compliance_levels))
                if compliance_levels[i] < compliance_levels[i-1]
            )
            consistency_factor = decreasing_count / (len(compliance_levels) - 1)
        else:
            consistency_factor = 0.5
        
        confidence = (
            observation_factor * 0.4 +
            variance_factor * 0.3 +
            consistency_factor * 0.3
        )
        
        return min(1.0, confidence)
    
    def get_active_drifts(
        self,
        category: Optional[ComplianceCategory] = None,
        min_severity: Optional[DriftSeverity] = None
    ) -> List[ComplianceDrift]:
        """Get active compliance drifts"""
        
        drifts = self.detected_drifts
        
        # Filter by category
        if category:
            drifts = [d for d in drifts if d.category == category]
        
        # Filter by severity
        if min_severity:
            severity_order = [
                DriftSeverity.NONE,
                DriftSeverity.MINOR,
                DriftSeverity.MODERATE,
                DriftSeverity.SIGNIFICANT,
                DriftSeverity.SEVERE
            ]
            min_index = severity_order.index(min_severity)
            drifts = [
                d for d in drifts
                if severity_order.index(d.severity) >= min_index
            ]
        
        # Sort by severity and drift magnitude
        severity_scores = {
            DriftSeverity.SEVERE: 5,
            DriftSeverity.SIGNIFICANT: 4,
            DriftSeverity.MODERATE: 3,
            DriftSeverity.MINOR: 2,
            DriftSeverity.NONE: 1
        }
        
        drifts.sort(
            key=lambda d: (severity_scores[d.severity], d.drift_magnitude),
            reverse=True
        )
        
        return drifts
    
    def get_compliance_health(self) -> Dict[str, Any]:
        """Get overall compliance health status"""
        
        if not self.baselines:
            return {
                'overall_health': 'unknown',
                'baselines_established': 0,
                'active_drifts': 0
            }
        
        # Calculate average current compliance
        current_levels = []
        for key, baseline in self.baselines.items():
            window = self.observation_windows[key]
            if window:
                recent_compliance = np.mean([
                    obs.actual_compliance
                    for obs in list(window)[-20:]
                ])
                current_levels.append(recent_compliance)
        
        avg_compliance = np.mean(current_levels) if current_levels else 0.0
        
        # Count drifts by severity
        drift_counts = {
            'severe': sum(1 for d in self.detected_drifts if d.severity == DriftSeverity.SEVERE),
            'significant': sum(1 for d in self.detected_drifts if d.severity == DriftSeverity.SIGNIFICANT),
            'moderate': sum(1 for d in self.detected_drifts if d.severity == DriftSeverity.MODERATE),
            'minor': sum(1 for d in self.detected_drifts if d.severity == DriftSeverity.MINOR)
        }
        
        # Determine overall health
        if drift_counts['severe'] > 0:
            overall_health = 'critical'
        elif drift_counts['significant'] > 0 or avg_compliance < 0.7:
            overall_health = 'poor'
        elif drift_counts['moderate'] > 2 or avg_compliance < 0.8:
            overall_health = 'fair'
        elif avg_compliance >= 0.9:
            overall_health = 'excellent'
        else:
            overall_health = 'good'
        
        return {
            'overall_health': overall_health,
            'average_compliance': avg_compliance,
            'baselines_established': len(self.baselines),
            'total_observations': len(self.observations),
            'active_drifts': len(self.detected_drifts),
            'drift_counts_by_severity': drift_counts,
            'most_at_risk_categories': self._identify_at_risk_categories()
        }
    
    def _identify_at_risk_categories(self) -> List[str]:
        """Identify compliance categories most at risk"""
        
        category_drift_scores = defaultdict(float)
        
        for drift in self.detected_drifts:
            severity_weights = {
                DriftSeverity.SEVERE: 5.0,
                DriftSeverity.SIGNIFICANT: 3.0,
                DriftSeverity.MODERATE: 2.0,
                DriftSeverity.MINOR: 1.0,
                DriftSeverity.NONE: 0.0
            }
            
            score = severity_weights[drift.severity] * drift.drift_magnitude
            category_drift_scores[drift.category.value] += score
        
        # Sort categories by risk score
        sorted_categories = sorted(
            category_drift_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [cat for cat, score in sorted_categories[:5]]


# Global intelligent compliance drift instance
intelligent_compliance_drift = IntelligentComplianceDrift()
