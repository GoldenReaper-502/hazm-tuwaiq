"""
HAZM TUWAIQ - Digital Safety Twin
Real-time virtual representation of safety state with simulation capabilities
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

from .models import (
    SafetyTwin as SafetyTwinModel,
    RiskLevel, TrendDirection
)


class SafetyTwin:
    """
    التوأم الرقمي للسلامة
    Digital twin for real-time safety monitoring and simulation
    """
    
    def __init__(self):
        """Initialize safety twin system"""
        self.logger = logging.getLogger(__name__)
        
        # Active twins registry
        self.twins: Dict[str, SafetyTwinModel] = {}
        
        # Real-time data streams
        self.data_streams: Dict[str, List[Dict]] = defaultdict(list)
        
        # Simulation scenarios
        self.scenarios: Dict[str, Dict[str, Any]] = {}
    
    def create_twin(
        self,
        twin_type: str,
        twin_name: str,
        real_entity_id: str,
        organization_id: str
    ) -> SafetyTwinModel:
        """
        Create new digital safety twin
        
        Args:
            twin_type: Type of twin (site, zone, worker, equipment)
            twin_name: Human-readable name
            real_entity_id: ID of real-world entity
            organization_id: Organization ID
            
        Returns:
            Created SafetyTwin instance
        """
        try:
            twin = SafetyTwinModel(
                twin_type=twin_type,
                twin_name=twin_name,
                real_entity_id=real_entity_id,
                organization_id=organization_id,
                safety_score=75.0,  # Initial baseline
                health_status="healthy"
            )
            
            # Register twin
            self.twins[twin.id] = twin
            
            self.logger.info(
                f"Safety twin created: {twin_name} ({twin_type}) - {twin.id}"
            )
            
            return twin
            
        except Exception as e:
            self.logger.error(f"Failed to create safety twin: {e}")
            raise
    
    def update_twin(
        self,
        twin_id: str,
        metrics: Dict[str, Any],
        environment: Optional[Dict[str, Any]] = None
    ) -> SafetyTwinModel:
        """
        Update twin with real-time data
        
        Args:
            twin_id: Twin ID
            metrics: Updated metrics
            environment: Environmental conditions
            
        Returns:
            Updated twin
        """
        try:
            twin = self.twins.get(twin_id)
            
            if not twin:
                raise ValueError(f"Twin not found: {twin_id}")
            
            # Update metrics
            if 'active_workers' in metrics:
                twin.active_workers = metrics['active_workers']
            if 'active_equipment' in metrics:
                twin.active_equipment = metrics['active_equipment']
            if 'active_alerts' in metrics:
                twin.active_alerts = metrics['active_alerts']
            if 'compliance_rate' in metrics:
                twin.compliance_rate = metrics['compliance_rate']
            
            # Update incidents
            if 'incidents_24h' in metrics:
                twin.incidents_24h = metrics['incidents_24h']
            if 'near_misses_24h' in metrics:
                twin.near_misses_24h = metrics['near_misses_24h']
            if 'safety_violations_24h' in metrics:
                twin.safety_violations_24h = metrics['safety_violations_24h']
            
            # Update environment
            if environment:
                twin.environment = environment
            
            # Recalculate safety score
            twin.safety_score = self._calculate_safety_score(twin)
            
            # Update health status
            twin.health_status = self._determine_health_status(twin)
            
            # Detect anomalies
            twin.current_anomalies = self._detect_anomalies(twin)
            
            # Generate recommendations
            twin.active_recommendations = self._generate_recommendations(twin)
            
            # Update risk prediction
            twin.predicted_risk_level = self._predict_risk_level(twin)
            twin.risk_trend = self._calculate_risk_trend(twin)
            twin.next_incident_probability = self._calculate_incident_probability(twin)
            
            # Update timestamp
            twin.last_updated = datetime.now()
            twin.sync_status = "synchronized"
            
            # Store in data stream
            self.data_streams[twin_id].append({
                'timestamp': datetime.now(),
                'safety_score': twin.safety_score,
                'health_status': twin.health_status
            })
            
            return twin
            
        except Exception as e:
            self.logger.error(f"Failed to update twin: {e}")
            raise
    
    def _calculate_safety_score(self, twin: SafetyTwinModel) -> float:
        """Calculate composite safety score (0-100)"""
        score = 100.0
        
        # Deduct for incidents
        score -= twin.incidents_24h * 10
        
        # Deduct for near misses
        score -= twin.near_misses_24h * 5
        
        # Deduct for violations
        score -= twin.safety_violations_24h * 3
        
        # Deduct for active alerts
        score -= twin.active_alerts * 2
        
        # Adjust for compliance
        score = score * (twin.compliance_rate / 100)
        
        # Ensure bounds
        score = max(0, min(100, score))
        
        return round(score, 2)
    
    def _determine_health_status(self, twin: SafetyTwinModel) -> str:
        """Determine health status from safety score"""
        if twin.safety_score >= 80:
            return "healthy"
        elif twin.safety_score >= 60:
            return "warning"
        else:
            return "critical"
    
    def _detect_anomalies(self, twin: SafetyTwinModel) -> List[str]:
        """Detect current anomalies"""
        anomalies = []
        
        # Check for unusual metrics
        if twin.incidents_24h > 3:
            anomalies.append("high_incident_rate")
        
        if twin.near_misses_24h > 10:
            anomalies.append("excessive_near_misses")
        
        if twin.compliance_rate < 70:
            anomalies.append("low_compliance")
        
        if twin.active_alerts > 5:
            anomalies.append("alert_flood")
        
        # Environmental anomalies
        if twin.environment:
            if twin.environment.get('temperature', 0) > 35:
                anomalies.append("high_temperature")
            if twin.environment.get('noise_level', 0) > 85:
                anomalies.append("excessive_noise")
        
        return anomalies
    
    def _generate_recommendations(self, twin: SafetyTwinModel) -> List[str]:
        """Generate active recommendations"""
        recommendations = []
        
        if twin.safety_score < 60:
            recommendations.append("🚨 Immediate safety audit required")
            recommendations.append("⚠️ Consider temporary work stoppage")
        
        if twin.incidents_24h > 2:
            recommendations.append("📊 Investigate incident root causes")
            recommendations.append("👥 Increase supervisor presence")
        
        if twin.compliance_rate < 80:
            recommendations.append("🎓 Conduct PPE compliance training")
            recommendations.append("🔍 Implement compliance monitoring")
        
        if twin.near_misses_24h > 5:
            recommendations.append("⚡ Review near-miss reports immediately")
            recommendations.append("🛠️ Check equipment and processes")
        
        return recommendations[:5]  # Top 5
    
    def _predict_risk_level(self, twin: SafetyTwinModel) -> RiskLevel:
        """Predict future risk level"""
        score = twin.safety_score
        
        if score >= 80:
            return RiskLevel.LOW
        elif score >= 70:
            return RiskLevel.MODERATE
        elif score >= 60:
            return RiskLevel.HIGH
        elif score >= 50:
            return RiskLevel.VERY_HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _calculate_risk_trend(self, twin: SafetyTwinModel) -> TrendDirection:
        """Calculate risk trend from history"""
        history = self.data_streams.get(twin.id, [])
        
        if len(history) < 5:
            return TrendDirection.STABLE
        
        # Compare recent vs older scores
        recent_scores = [h['safety_score'] for h in history[-5:]]
        older_scores = [h['safety_score'] for h in history[-10:-5]] if len(history) >= 10 else recent_scores
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores)
        
        change = recent_avg - older_avg
        
        if change > 5:
            return TrendDirection.IMPROVING
        elif change < -5:
            return TrendDirection.DEGRADING
        else:
            return TrendDirection.STABLE
    
    def _calculate_incident_probability(self, twin: SafetyTwinModel) -> float:
        """Calculate probability of next incident"""
        base_prob = 0.1
        
        # Adjust for recent incidents
        base_prob += twin.incidents_24h * 0.15
        
        # Adjust for near misses
        base_prob += twin.near_misses_24h * 0.05
        
        # Adjust for violations
        base_prob += twin.safety_violations_24h * 0.03
        
        # Adjust for compliance
        base_prob *= (1 - twin.compliance_rate / 100)
        
        return min(base_prob, 1.0)
    
    def simulate_scenario(
        self,
        twin_id: str,
        scenario_name: str,
        interventions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulate what-if scenario
        
        Args:
            twin_id: Twin to simulate
            scenario_name: Scenario name
            interventions: Proposed interventions
            
        Returns:
            Simulation results
        """
        try:
            twin = self.twins.get(twin_id)
            
            if not twin:
                raise ValueError(f"Twin not found: {twin_id}")
            
            # Create simulated twin (copy)
            sim_twin = SafetyTwinModel(**twin.dict())
            
            # Apply interventions
            results = {
                'scenario': scenario_name,
                'baseline_score': twin.safety_score,
                'baseline_risk': twin.predicted_risk_level.value,
                'interventions_applied': [],
                'projected_score': twin.safety_score,
                'projected_risk': twin.predicted_risk_level.value,
                'risk_reduction': 0.0,
                'estimated_cost': 'medium',
                'implementation_time': '2 weeks'
            }
            
            # Simulate interventions
            if 'increase_supervision' in interventions:
                sim_twin.compliance_rate = min(sim_twin.compliance_rate + 15, 100)
                sim_twin.safety_violations_24h = max(sim_twin.safety_violations_24h - 2, 0)
                results['interventions_applied'].append('increase_supervision')
            
            if 'additional_training' in interventions:
                sim_twin.compliance_rate = min(sim_twin.compliance_rate + 10, 100)
                results['interventions_applied'].append('additional_training')
            
            if 'equipment_upgrade' in interventions:
                sim_twin.incidents_24h = max(sim_twin.incidents_24h - 1, 0)
                results['interventions_applied'].append('equipment_upgrade')
                results['estimated_cost'] = 'high'
            
            if 'enhanced_monitoring' in interventions:
                sim_twin.near_misses_24h = max(sim_twin.near_misses_24h - 3, 0)
                results['interventions_applied'].append('enhanced_monitoring')
            
            # Recalculate after interventions
            sim_twin.safety_score = self._calculate_safety_score(sim_twin)
            sim_twin.predicted_risk_level = self._predict_risk_level(sim_twin)
            
            # Update results
            results['projected_score'] = sim_twin.safety_score
            results['projected_risk'] = sim_twin.predicted_risk_level.value
            results['risk_reduction'] = round(
                (sim_twin.safety_score - twin.safety_score) / 100, 2
            )
            
            # Store scenario
            self.scenarios[f"{twin_id}_{scenario_name}"] = results
            
            self.logger.info(
                f"Scenario simulated: {scenario_name} - "
                f"Score: {twin.safety_score:.1f} → {sim_twin.safety_score:.1f}"
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to simulate scenario: {e}")
            raise
    
    def get_twin(self, twin_id: str) -> Optional[SafetyTwinModel]:
        """Get twin by ID"""
        return self.twins.get(twin_id)
    
    def get_all_twins(
        self,
        organization_id: str,
        twin_type: Optional[str] = None
    ) -> List[SafetyTwinModel]:
        """Get all twins for organization"""
        twins = [
            t for t in self.twins.values()
            if t.organization_id == organization_id
        ]
        
        if twin_type:
            twins = [t for t in twins if t.twin_type == twin_type]
        
        return twins
    
    def get_stats(self) -> Dict[str, Any]:
        """Get digital twin statistics"""
        all_twins = list(self.twins.values())
        
        if not all_twins:
            return {
                'total_twins': 0,
                'by_type': {},
                'by_health': {},
                'average_safety_score': 0.0
            }
        
        stats = {
            'total_twins': len(all_twins),
            'by_type': {},
            'by_health': {},
            'average_safety_score': round(
                sum(t.safety_score for t in all_twins) / len(all_twins), 2
            ),
            'simulations_run': len(self.scenarios)
        }
        
        # Count by type
        for twin in all_twins:
            stats['by_type'][twin.twin_type] = stats['by_type'].get(twin.twin_type, 0) + 1
            stats['by_health'][twin.health_status] = stats['by_health'].get(twin.health_status, 0) + 1
        
        return stats


# Singleton instance
_safety_twin: Optional[SafetyTwin] = None


def get_safety_twin() -> SafetyTwin:
    """Get singleton SafetyTwin instance"""
    global _safety_twin
    
    if _safety_twin is None:
        _safety_twin = SafetyTwin()
    
    return _safety_twin
