"""
HAZM TUWAIQ - Predictive Maintenance
AI-powered equipment failure prediction and maintenance optimization
Prevents accidents through proactive equipment monitoring
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
import numpy as np


class EquipmentType(str, Enum):
    """Types of equipment"""
    MACHINERY = "machinery"
    VEHICLE = "vehicle"
    TOOL = "tool"
    SAFETY_EQUIPMENT = "safety_equipment"
    HVAC = "hvac"
    ELECTRICAL = "electrical"
    LIFTING = "lifting"
    SCAFFOLD = "scaffold"
    FALL_PROTECTION = "fall_protection"


class HealthStatus(str, Enum):
    """Equipment health status"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"
    FAILED = "failed"


class MaintenancePriority(str, Enum):
    """Maintenance priority levels"""
    ROUTINE = "routine"
    SCHEDULED = "scheduled"
    URGENT = "urgent"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class SensorData:
    """Equipment sensor reading"""
    equipment_id: str
    timestamp: datetime
    sensor_type: str  # temperature, vibration, pressure, current, etc.
    value: float
    unit: str
    normal_range_min: float
    normal_range_max: float
    

@dataclass
class MaintenanceRecord:
    """Historical maintenance record"""
    record_id: str
    equipment_id: str
    date: datetime
    maintenance_type: str  # preventive, corrective, emergency
    description: str
    cost: float
    downtime_hours: float
    parts_replaced: List[str]
    

@dataclass
class FailurePrediction:
    """Equipment failure prediction"""
    equipment_id: str
    prediction_date: datetime
    predicted_failure_date: datetime
    days_until_failure: int
    failure_probability: float  # 0-1
    failure_mode: str
    contributing_factors: List[str]
    recommended_actions: List[str]
    estimated_cost_if_ignored: float
    estimated_preventive_cost: float
    roi: float  # Return on investment
    confidence: float


@dataclass
class Equipment:
    """Equipment asset"""
    equipment_id: str
    name: str
    equipment_type: EquipmentType
    model: str
    manufacturer: str
    installation_date: datetime
    last_maintenance: Optional[datetime]
    next_scheduled_maintenance: Optional[datetime]
    health_status: HealthStatus
    health_score: float  # 0-100
    operating_hours: float
    mtbf: Optional[float]  # Mean Time Between Failures
    mttr: Optional[float]  # Mean Time To Repair
    failure_count: int
    

class PredictiveMaintenance:
    """
    AI-powered predictive maintenance system
    
    Features:
    - Real-time equipment health monitoring
    - Failure prediction using sensor data and historical patterns
    - Optimal maintenance scheduling
    - Cost-benefit analysis
    - Safety-critical equipment prioritization
    """
    
    def __init__(self):
        self.equipment_registry: Dict[str, Equipment] = {}
        self.sensor_data: List[SensorData] = []
        self.maintenance_history: List[MaintenanceRecord] = []
        self.failure_predictions: List[FailurePrediction] = []
        
        # Degradation models (how fast different equipment types degrade)
        self.degradation_rates = {
            EquipmentType.MACHINERY: 0.15,  # % per month
            EquipmentType.VEHICLE: 0.20,
            EquipmentType.TOOL: 0.10,
            EquipmentType.SAFETY_EQUIPMENT: 0.05,  # Safety equipment degrades slowly but is critical
            EquipmentType.HVAC: 0.12,
            EquipmentType.ELECTRICAL: 0.08,
            EquipmentType.LIFTING: 0.10,
            EquipmentType.SCAFFOLD: 0.06,
            EquipmentType.FALL_PROTECTION: 0.04
        }
        
        # Failure impact (safety criticality)
        self.safety_criticality = {
            EquipmentType.FALL_PROTECTION: 10.0,  # Highest criticality
            EquipmentType.LIFTING: 9.0,
            EquipmentType.SCAFFOLD: 8.5,
            EquipmentType.SAFETY_EQUIPMENT: 8.0,
            EquipmentType.MACHINERY: 7.0,
            EquipmentType.VEHICLE: 6.5,
            EquipmentType.ELECTRICAL: 6.0,
            EquipmentType.HVAC: 4.0,
            EquipmentType.TOOL: 3.0
        }
    
    def register_equipment(
        self,
        equipment_id: str,
        name: str,
        equipment_type: EquipmentType,
        model: str,
        manufacturer: str,
        installation_date: datetime
    ):
        """Register new equipment in system"""
        
        self.equipment_registry[equipment_id] = Equipment(
            equipment_id=equipment_id,
            name=name,
            equipment_type=equipment_type,
            model=model,
            manufacturer=manufacturer,
            installation_date=installation_date,
            last_maintenance=None,
            next_scheduled_maintenance=None,
            health_status=HealthStatus.EXCELLENT,
            health_score=100.0,
            operating_hours=0.0,
            mtbf=None,
            mttr=None,
            failure_count=0
        )
    
    def ingest_sensor_data(self, data: SensorData):
        """Ingest real-time sensor data"""
        
        self.sensor_data.append(data)
        
        # Update equipment health based on sensor data
        self._update_equipment_health(data)
    
    def record_maintenance(self, record: MaintenanceRecord):
        """Record completed maintenance"""
        
        self.maintenance_history.append(record)
        
        equipment = self.equipment_registry.get(record.equipment_id)
        if equipment:
            equipment.last_maintenance = record.date
            
            # If preventive maintenance, boost health score
            if record.maintenance_type == "preventive":
                equipment.health_score = min(100.0, equipment.health_score + 15.0)
                equipment.health_status = self._get_health_status(equipment.health_score)
            
            # Calculate MTBF and MTTR
            self._update_reliability_metrics(record.equipment_id)
    
    def _update_equipment_health(self, data: SensorData):
        """Update equipment health based on sensor reading"""
        
        equipment = self.equipment_registry.get(data.equipment_id)
        if not equipment:
            return
        
        # Check if reading is out of normal range
        if data.value < data.normal_range_min or data.value > data.normal_range_max:
            # Calculate severity of deviation
            if data.value < data.normal_range_min:
                deviation = (data.normal_range_min - data.value) / data.normal_range_min
            else:
                deviation = (data.value - data.normal_range_max) / data.normal_range_max
            
            # Penalize health score
            penalty = min(10.0, deviation * 20.0)
            equipment.health_score = max(0.0, equipment.health_score - penalty)
            equipment.health_status = self._get_health_status(equipment.health_score)
    
    def _get_health_status(self, health_score: float) -> HealthStatus:
        """Convert health score to status"""
        
        if health_score >= 85:
            return HealthStatus.EXCELLENT
        elif health_score >= 70:
            return HealthStatus.GOOD
        elif health_score >= 50:
            return HealthStatus.FAIR
        elif health_score >= 30:
            return HealthStatus.POOR
        elif health_score > 0:
            return HealthStatus.CRITICAL
        else:
            return HealthStatus.FAILED
    
    def predict_failures(self, equipment_id: Optional[str] = None) -> List[FailurePrediction]:
        """
        Predict equipment failures
        
        Args:
            equipment_id: Specific equipment to analyze, or None for all
        """
        
        equipment_to_analyze = []
        
        if equipment_id:
            if equipment_id in self.equipment_registry:
                equipment_to_analyze = [self.equipment_registry[equipment_id]]
        else:
            equipment_to_analyze = list(self.equipment_registry.values())
        
        predictions = []
        
        for equipment in equipment_to_analyze:
            prediction = self._predict_single_failure(equipment)
            if prediction:
                predictions.append(prediction)
        
        # Sort by urgency (days until failure * failure probability)
        predictions.sort(key=lambda p: p.days_until_failure * (1 - p.failure_probability))
        
        return predictions
    
    def _predict_single_failure(self, equipment: Equipment) -> Optional[FailurePrediction]:
        """Predict failure for single equipment"""
        
        # Get recent sensor data
        cutoff = datetime.now() - timedelta(days=30)
        recent_sensors = [
            s for s in self.sensor_data
            if s.equipment_id == equipment.equipment_id and s.timestamp >= cutoff
        ]
        
        # Factors affecting failure prediction
        factors = []
        failure_probability = 0.0
        
        # Factor 1: Health score
        if equipment.health_score < 70:
            health_factor = (100 - equipment.health_score) / 100.0
            failure_probability += health_factor * 0.4
            factors.append(f"Low health score ({equipment.health_score:.0f}/100)")
        
        # Factor 2: Sensor anomalies
        if recent_sensors:
            anomaly_count = sum(
                1 for s in recent_sensors
                if s.value < s.normal_range_min or s.value > s.normal_range_max
            )
            anomaly_rate = anomaly_count / len(recent_sensors)
            
            if anomaly_rate > 0.1:  # More than 10% anomalies
                failure_probability += anomaly_rate * 0.3
                factors.append(f"Sensor anomalies ({anomaly_rate*100:.0f}% of readings)")
        
        # Factor 3: Age and operating hours
        age_days = (datetime.now() - equipment.installation_date).days
        age_years = age_days / 365.0
        
        # Expected lifespan by type (years)
        expected_lifespans = {
            EquipmentType.MACHINERY: 10,
            EquipmentType.VEHICLE: 8,
            EquipmentType.TOOL: 5,
            EquipmentType.SAFETY_EQUIPMENT: 3,
            EquipmentType.HVAC: 15,
            EquipmentType.ELECTRICAL: 20,
            EquipmentType.LIFTING: 12,
            EquipmentType.SCAFFOLD: 10,
            EquipmentType.FALL_PROTECTION: 2
        }
        
        expected_life = expected_lifespans.get(equipment.equipment_type, 10)
        age_factor = age_years / expected_life
        
        if age_factor > 0.7:  # Over 70% of expected life
            failure_probability += age_factor * 0.2
            factors.append(f"Age ({age_years:.1f} years, {age_factor*100:.0f}% of expected life)")
        
        # Factor 4: Maintenance history
        if equipment.last_maintenance:
            days_since_maintenance = (datetime.now() - equipment.last_maintenance).days
            
            # Expected maintenance interval (days)
            maintenance_intervals = {
                EquipmentType.MACHINERY: 90,
                EquipmentType.VEHICLE: 180,
                EquipmentType.TOOL: 365,
                EquipmentType.SAFETY_EQUIPMENT: 90,
                EquipmentType.HVAC: 180,
                EquipmentType.ELECTRICAL: 365,
                EquipmentType.LIFTING: 90,
                EquipmentType.SCAFFOLD: 180,
                EquipmentType.FALL_PROTECTION: 60
            }
            
            expected_interval = maintenance_intervals.get(equipment.equipment_type, 180)
            
            if days_since_maintenance > expected_interval * 1.2:  # 20% overdue
                maintenance_factor = (days_since_maintenance - expected_interval) / expected_interval
                failure_probability += min(0.3, maintenance_factor * 0.1)
                factors.append(f"Maintenance overdue ({days_since_maintenance} days since last)")
        else:
            # Never maintained
            failure_probability += 0.2
            factors.append("No maintenance history")
        
        # Factor 5: Failure history
        if equipment.mtbf and equipment.operating_hours > equipment.mtbf * 0.9:
            failure_probability += 0.3
            factors.append(f"Approaching MTBF ({equipment.operating_hours:.0f} hrs vs {equipment.mtbf:.0f} hrs)")
        
        # Only create prediction if probability > 30%
        if failure_probability < 0.3:
            return None
        
        # Predict days until failure (inverse of probability, scaled by health)
        base_days = 60  # Base prediction window
        days_until_failure = int(base_days * (1 - failure_probability) * (equipment.health_score / 100.0))
        days_until_failure = max(1, days_until_failure)  # At least 1 day
        
        # Estimate costs
        safety_factor = self.safety_criticality.get(equipment.equipment_type, 5.0)
        
        # Cost if failure happens (unplanned)
        base_repair_cost = 5000.0  # Base repair cost
        cost_if_ignored = base_repair_cost * (1.5 + safety_factor * 0.2)  # Higher for safety-critical
        
        # Cost of preventive maintenance
        preventive_cost = base_repair_cost * 0.6  # 60% of repair cost
        
        # ROI
        roi = (cost_if_ignored - preventive_cost) / preventive_cost
        
        # Determine failure mode
        failure_mode = self._determine_failure_mode(equipment, recent_sensors)
        
        # Recommended actions
        recommended_actions = self._generate_maintenance_recommendations(
            equipment,
            failure_probability,
            days_until_failure
        )
        
        return FailurePrediction(
            equipment_id=equipment.equipment_id,
            prediction_date=datetime.now(),
            predicted_failure_date=datetime.now() + timedelta(days=days_until_failure),
            days_until_failure=days_until_failure,
            failure_probability=min(1.0, failure_probability),
            failure_mode=failure_mode,
            contributing_factors=factors,
            recommended_actions=recommended_actions,
            estimated_cost_if_ignored=cost_if_ignored,
            estimated_preventive_cost=preventive_cost,
            roi=roi,
            confidence=0.7 if len(recent_sensors) > 10 else 0.5
        )
    
    def _determine_failure_mode(
        self,
        equipment: Equipment,
        recent_sensors: List[SensorData]
    ) -> str:
        """Determine most likely failure mode"""
        
        if not recent_sensors:
            return "unknown_degradation"
        
        # Analyze sensor patterns
        sensor_types = defaultdict(list)
        for sensor in recent_sensors:
            sensor_types[sensor.sensor_type].append(sensor.value)
        
        # Check for specific failure modes
        if 'temperature' in sensor_types:
            temps = sensor_types['temperature']
            if np.mean(temps) > 80:  # High temperature
                return "thermal_failure"
        
        if 'vibration' in sensor_types:
            vibs = sensor_types['vibration']
            if np.mean(vibs) > 10:  # High vibration
                return "mechanical_wear"
        
        if 'pressure' in sensor_types:
            pressures = sensor_types['pressure']
            if any(p < 0 for p in pressures):  # Negative pressure
                return "seal_failure"
        
        # Default based on equipment type
        default_modes = {
            EquipmentType.MACHINERY: "mechanical_wear",
            EquipmentType.VEHICLE: "component_fatigue",
            EquipmentType.TOOL: "wear_and_tear",
            EquipmentType.SAFETY_EQUIPMENT: "material_degradation",
            EquipmentType.HVAC: "filter_clogging",
            EquipmentType.ELECTRICAL: "insulation_breakdown",
            EquipmentType.LIFTING: "cable_wear",
            EquipmentType.SCAFFOLD: "structural_fatigue",
            EquipmentType.FALL_PROTECTION: "strap_degradation"
        }
        
        return default_modes.get(equipment.equipment_type, "general_degradation")
    
    def _generate_maintenance_recommendations(
        self,
        equipment: Equipment,
        failure_probability: float,
        days_until_failure: int
    ) -> List[str]:
        """Generate maintenance recommendations"""
        
        recommendations = []
        
        # Urgency-based recommendations
        if days_until_failure < 7:
            recommendations.append("URGENT: Schedule maintenance within 48 hours")
            recommendations.append("Consider taking equipment out of service immediately")
        elif days_until_failure < 14:
            recommendations.append("Schedule maintenance within next week")
            recommendations.append("Increase inspection frequency to daily")
        elif days_until_failure < 30:
            recommendations.append("Plan maintenance within next 2 weeks")
            recommendations.append("Monitor sensor data closely")
        else:
            recommendations.append("Schedule routine maintenance")
        
        # Equipment-specific recommendations
        if equipment.equipment_type in [EquipmentType.FALL_PROTECTION, EquipmentType.LIFTING]:
            recommendations.append("Perform detailed safety inspection before next use")
            recommendations.append("Consider backup equipment during maintenance")
        
        # Health-based recommendations
        if equipment.health_score < 50:
            recommendations.append("Full diagnostic assessment recommended")
            recommendations.append("Consider replacement if repair cost > 60% of new equipment")
        
        return recommendations
    
    def _update_reliability_metrics(self, equipment_id: str):
        """Update MTBF and MTTR metrics"""
        
        equipment = self.equipment_registry.get(equipment_id)
        if not equipment:
            return
        
        # Get all maintenance records
        records = [r for r in self.maintenance_history if r.equipment_id == equipment_id]
        
        if len(records) < 2:
            return
        
        # Calculate MTBF (Mean Time Between Failures)
        failure_records = [r for r in records if r.maintenance_type in ['corrective', 'emergency']]
        
        if len(failure_records) >= 2:
            # Sort by date
            failure_records.sort(key=lambda r: r.date)
            
            # Calculate time between failures
            time_between = []
            for i in range(1, len(failure_records)):
                delta = (failure_records[i].date - failure_records[i-1].date).days
                time_between.append(delta)
            
            equipment.mtbf = np.mean(time_between) * 24.0  # Convert to hours
        
        # Calculate MTTR (Mean Time To Repair)
        downtimes = [r.downtime_hours for r in records if r.downtime_hours > 0]
        if downtimes:
            equipment.mttr = np.mean(downtimes)
    
    def optimize_maintenance_schedule(self) -> List[Dict[str, Any]]:
        """Optimize maintenance schedule across all equipment"""
        
        # Get all failure predictions
        predictions = self.predict_failures()
        
        # Prioritize by:
        # 1. Safety criticality
        # 2. Failure probability
        # 3. Days until failure
        # 4. ROI
        
        prioritized = []
        
        for pred in predictions:
            equipment = self.equipment_registry[pred.equipment_id]
            
            # Calculate priority score
            safety_score = self.safety_criticality.get(equipment.equipment_type, 5.0)
            urgency_score = 1.0 / max(1, pred.days_until_failure)
            probability_score = pred.failure_probability
            roi_score = min(10.0, pred.roi) / 10.0  # Normalize to 0-1
            
            priority_score = (
                safety_score * 0.4 +
                urgency_score * 100 * 0.3 +
                probability_score * 100 * 0.2 +
                roi_score * 100 * 0.1
            )
            
            prioritized.append({
                'equipment_id': pred.equipment_id,
                'equipment_name': equipment.name,
                'equipment_type': equipment.equipment_type.value,
                'days_until_failure': pred.days_until_failure,
                'failure_probability': pred.failure_probability,
                'priority_score': priority_score,
                'priority': self._get_maintenance_priority(priority_score),
                'recommended_date': datetime.now() + timedelta(days=min(7, pred.days_until_failure // 2)),
                'estimated_cost': pred.estimated_preventive_cost,
                'roi': pred.roi,
                'actions': pred.recommended_actions
            })
        
        # Sort by priority score
        prioritized.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return prioritized
    
    def _get_maintenance_priority(self, priority_score: float) -> MaintenancePriority:
        """Convert priority score to priority level"""
        
        if priority_score >= 80:
            return MaintenancePriority.EMERGENCY
        elif priority_score >= 60:
            return MaintenancePriority.CRITICAL
        elif priority_score >= 40:
            return MaintenancePriority.URGENT
        elif priority_score >= 20:
            return MaintenancePriority.SCHEDULED
        else:
            return MaintenancePriority.ROUTINE
    
    def get_fleet_health_report(self) -> Dict[str, Any]:
        """Get overall fleet health report"""
        
        total_equipment = len(self.equipment_registry)
        
        if total_equipment == 0:
            return {
                'total_equipment': 0,
                'average_health': 0.0,
                'equipment_by_status': {},
                'critical_count': 0,
                'predictions_count': 0
            }
        
        # Equipment by health status
        status_counts = defaultdict(int)
        total_health = 0.0
        
        for equipment in self.equipment_registry.values():
            status_counts[equipment.health_status.value] += 1
            total_health += equipment.health_score
        
        # Get predictions
        predictions = self.predict_failures()
        
        # Critical equipment (failure in < 7 days)
        critical_predictions = [p for p in predictions if p.days_until_failure < 7]
        
        return {
            'total_equipment': total_equipment,
            'average_health': total_health / total_equipment,
            'equipment_by_status': dict(status_counts),
            'critical_count': status_counts[HealthStatus.CRITICAL.value] + status_counts[HealthStatus.POOR.value],
            'predictions_count': len(predictions),
            'urgent_maintenance_needed': len(critical_predictions),
            'total_estimated_savings': sum(p.roi * p.estimated_preventive_cost for p in predictions),
            'maintenance_schedule': self.optimize_maintenance_schedule()[:10]  # Top 10
        }


# Global predictive maintenance instance
predictive_maintenance = PredictiveMaintenance()
