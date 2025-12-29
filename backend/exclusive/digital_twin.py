"""
HAZM TUWAIQ - Enhanced Digital Twin System
Real-time digital replica of entire safety infrastructure
Predictive simulation and what-if analysis
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
import numpy as np


class AssetType(str, Enum):
    """Types of assets in digital twin"""
    WORKER = "worker"
    EQUIPMENT = "equipment"
    ZONE = "zone"
    VEHICLE = "vehicle"
    BUILDING = "building"
    SENSOR = "sensor"
    SAFETY_SYSTEM = "safety_system"


class SimulationScenario(str, Enum):
    """Types of simulation scenarios"""
    NORMAL_OPERATIONS = "normal_operations"
    EQUIPMENT_FAILURE = "equipment_failure"
    WEATHER_EVENT = "weather_event"
    EMERGENCY_EVACUATION = "emergency_evacuation"
    PROCESS_CHANGE = "process_change"
    CAPACITY_TEST = "capacity_test"


@dataclass
class DigitalAsset:
    """Digital twin of a physical asset"""
    asset_id: str
    asset_type: AssetType
    name: str
    location: Dict[str, float]  # x, y, z coordinates
    properties: Dict[str, Any]
    state: Dict[str, Any]
    last_updated: datetime
    health_score: float = 100.0
    

@dataclass
class SimulationResult:
    """Result of a what-if simulation"""
    simulation_id: str
    scenario: SimulationScenario
    parameters: Dict[str, Any]
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    predicted_outcomes: List[Dict[str, Any]]
    risk_assessment: Dict[str, float]
    recommendations: List[str]
    confidence: float
    

class EnhancedDigitalTwin:
    """
    Enhanced digital twin system for comprehensive safety modeling
    
    Features:
    - Real-time synchronization with physical world
    - Predictive simulation (what-if analysis)
    - Historical replay
    - Risk heatmap generation
    - Capacity and bottleneck analysis
    - Emergency scenario planning
    """
    
    def __init__(self):
        self.assets: Dict[str, DigitalAsset] = {}
        self.asset_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.simulations: List[SimulationResult] = []
        
        # Twin synchronization status
        self.sync_status = {
            'last_sync': None,
            'sync_latency_ms': 0.0,
            'assets_in_sync': 0,
            'total_assets': 0
        }
    
    def register_asset(
        self,
        asset_id: str,
        asset_type: AssetType,
        name: str,
        location: Dict[str, float],
        properties: Optional[Dict[str, Any]] = None
    ):
        """Register a new asset in the digital twin"""
        
        self.assets[asset_id] = DigitalAsset(
            asset_id=asset_id,
            asset_type=asset_type,
            name=name,
            location=location,
            properties=properties or {},
            state={},
            last_updated=datetime.now(),
            health_score=100.0
        )
        
        self.sync_status['total_assets'] += 1
    
    def update_asset_state(
        self,
        asset_id: str,
        state_update: Dict[str, Any]
    ):
        """Update asset state in real-time"""
        
        if asset_id not in self.assets:
            return
        
        asset = self.assets[asset_id]
        
        # Store historical state
        self.asset_history[asset_id].append({
            'timestamp': datetime.now(),
            'state': asset.state.copy()
        })
        
        # Update current state
        asset.state.update(state_update)
        asset.last_updated = datetime.now()
        
        # Update sync status
        self.sync_status['last_sync'] = datetime.now()
        self.sync_status['assets_in_sync'] = sum(
            1 for a in self.assets.values()
            if (datetime.now() - a.last_updated).total_seconds() < 60
        )
    
    def update_asset_location(
        self,
        asset_id: str,
        new_location: Dict[str, float]
    ):
        """Update asset location"""
        
        if asset_id not in self.assets:
            return
        
        # Store historical location
        self.asset_history[asset_id].append({
            'timestamp': datetime.now(),
            'location': self.assets[asset_id].location.copy()
        })
        
        self.assets[asset_id].location = new_location
        self.assets[asset_id].last_updated = datetime.now()
    
    def simulate_scenario(
        self,
        scenario: SimulationScenario,
        parameters: Dict[str, Any],
        duration_minutes: int = 60
    ) -> SimulationResult:
        """
        Simulate a what-if scenario
        
        Predicts outcomes based on current state and scenario parameters
        """
        
        start_time = datetime.now()
        
        # Get current state snapshot
        current_state = {
            asset_id: {
                'location': asset.location.copy(),
                'state': asset.state.copy(),
                'health': asset.health_score
            }
            for asset_id, asset in self.assets.items()
        }
        
        # Run scenario-specific simulation
        if scenario == SimulationScenario.EQUIPMENT_FAILURE:
            outcomes = self._simulate_equipment_failure(current_state, parameters)
        elif scenario == SimulationScenario.EMERGENCY_EVACUATION:
            outcomes = self._simulate_evacuation(current_state, parameters)
        elif scenario == SimulationScenario.WEATHER_EVENT:
            outcomes = self._simulate_weather_event(current_state, parameters)
        elif scenario == SimulationScenario.CAPACITY_TEST:
            outcomes = self._simulate_capacity_test(current_state, parameters)
        else:
            outcomes = self._simulate_normal_operations(current_state, parameters)
        
        # Assess risks
        risk_assessment = self._assess_simulation_risks(outcomes)
        
        # Generate recommendations
        recommendations = self._generate_simulation_recommendations(outcomes, risk_assessment)
        
        # Calculate confidence
        confidence = self._calculate_simulation_confidence(current_state, parameters)
        
        end_time = datetime.now()
        
        result = SimulationResult(
            simulation_id=f"SIM-{len(self.simulations) + 1:06d}",
            scenario=scenario,
            parameters=parameters,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=(end_time - start_time).total_seconds(),
            predicted_outcomes=outcomes,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            confidence=confidence
        )
        
        self.simulations.append(result)
        
        return result
    
    def _simulate_equipment_failure(
        self,
        current_state: Dict[str, Dict],
        parameters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Simulate equipment failure scenario"""
        
        failed_equipment = parameters.get('equipment_id')
        failure_type = parameters.get('failure_type', 'sudden_stop')
        
        outcomes = []
        
        # Identify affected workers
        affected_workers = self._find_workers_near_equipment(
            failed_equipment,
            radius_meters=parameters.get('impact_radius', 10.0)
        )
        
        outcomes.append({
            'event': 'equipment_failure',
            'equipment': failed_equipment,
            'failure_type': failure_type,
            'affected_workers': len(affected_workers),
            'worker_ids': [w for w in affected_workers],
            'estimated_downtime_hours': self._estimate_downtime(failure_type),
            'safety_risk': 'high' if len(affected_workers) > 0 else 'low'
        })
        
        # Simulate cascading effects
        if failure_type == 'fire':
            outcomes.append({
                'event': 'fire_spread',
                'origin': failed_equipment,
                'estimated_spread_rate': 0.5,  # meters per minute
                'evacuation_required': True,
                'fire_suppression_response_time': 120  # seconds
            })
        
        # Production impact
        outcomes.append({
            'event': 'production_impact',
            'downtime_cost_per_hour': 5000.0,
            'total_estimated_cost': 5000.0 * self._estimate_downtime(failure_type)
        })
        
        return outcomes
    
    def _simulate_evacuation(
        self,
        current_state: Dict[str, Dict],
        parameters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Simulate emergency evacuation"""
        
        evacuation_zone = parameters.get('zone')
        threat_type = parameters.get('threat', 'general')
        
        # Find all workers in zone
        workers_in_zone = [
            asset_id for asset_id, asset in self.assets.items()
            if asset.asset_type == AssetType.WORKER and
            self._is_in_zone(asset.location, evacuation_zone)
        ]
        
        # Simulate evacuation flow
        exit_points = parameters.get('exit_points', 2)
        evacuation_rate = 1.5  # people per second per exit
        
        total_evacuation_time = len(workers_in_zone) / (evacuation_rate * exit_points)
        
        outcomes = [{
            'event': 'evacuation_complete',
            'total_workers': len(workers_in_zone),
            'exit_points_used': exit_points,
            'estimated_evacuation_time_seconds': total_evacuation_time,
            'bottlenecks': self._identify_evacuation_bottlenecks(workers_in_zone, exit_points),
            'at_risk_workers': [
                w for w in workers_in_zone
                if self._calculate_evacuation_risk(w, evacuation_zone) > 0.7
            ]
        }]
        
        return outcomes
    
    def _simulate_weather_event(
        self,
        current_state: Dict[str, Dict],
        parameters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Simulate weather impact"""
        
        weather_type = parameters.get('weather_type', 'high_wind')
        intensity = parameters.get('intensity', 0.5)  # 0-1
        
        outcomes = []
        
        # Identify outdoor assets at risk
        outdoor_assets = [
            asset_id for asset_id, asset in self.assets.items()
            if asset.properties.get('location_type') == 'outdoor'
        ]
        
        # Calculate impact
        if weather_type == 'high_wind':
            at_risk_equipment = [
                aid for aid in outdoor_assets
                if self.assets[aid].asset_type in [AssetType.EQUIPMENT, AssetType.VEHICLE]
            ]
            
            outcomes.append({
                'event': 'wind_damage_risk',
                'at_risk_assets': len(at_risk_equipment),
                'recommended_actions': ['Secure loose equipment', 'Halt crane operations'],
                'estimated_damage_cost': len(at_risk_equipment) * 1000.0 * intensity
            })
        
        # Worker safety impact
        outdoor_workers = [
            aid for aid in outdoor_assets
            if self.assets[aid].asset_type == AssetType.WORKER
        ]
        
        outcomes.append({
            'event': 'worker_exposure',
            'exposed_workers': len(outdoor_workers),
            'recommended_action': 'Move workers to shelter' if intensity > 0.6 else 'Monitor conditions'
        })
        
        return outcomes
    
    def _simulate_capacity_test(
        self,
        current_state: Dict[str, Dict],
        parameters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Simulate capacity and bottleneck testing"""
        
        target_capacity = parameters.get('target_workers', 50)
        zone = parameters.get('zone', 'main_area')
        
        # Calculate current capacity
        current_workers = sum(
            1 for asset in self.assets.values()
            if asset.asset_type == AssetType.WORKER
        )
        
        capacity_factor = target_capacity / max(1, current_workers)
        
        outcomes = [{
            'event': 'capacity_analysis',
            'current_workers': current_workers,
            'target_workers': target_capacity,
            'capacity_factor': capacity_factor,
            'bottlenecks': self._identify_capacity_bottlenecks(target_capacity),
            'safety_concerns': [] if capacity_factor < 1.5 else [
                'Overcrowding risk',
                'Exit capacity insufficient',
                'Equipment overload'
            ]
        }]
        
        return outcomes
    
    def _simulate_normal_operations(
        self,
        current_state: Dict[str, Dict],
        parameters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Simulate normal operations"""
        
        forecast_hours = parameters.get('forecast_hours', 8)
        
        # Predict equipment health degradation
        equipment_predictions = []
        
        for asset_id, asset in self.assets.items():
            if asset.asset_type == AssetType.EQUIPMENT:
                # Simple linear degradation model
                current_health = asset.health_score
                degradation_rate = 0.5  # % per hour
                predicted_health = max(0, current_health - degradation_rate * forecast_hours)
                
                equipment_predictions.append({
                    'equipment_id': asset_id,
                    'current_health': current_health,
                    'predicted_health': predicted_health,
                    'maintenance_needed': predicted_health < 70.0
                })
        
        outcomes = [{
            'event': 'operational_forecast',
            'forecast_period_hours': forecast_hours,
            'equipment_health_predictions': equipment_predictions,
            'predicted_incidents': len([e for e in equipment_predictions if e['maintenance_needed']]) * 0.1
        }]
        
        return outcomes
    
    def _find_workers_near_equipment(
        self,
        equipment_id: str,
        radius_meters: float
    ) -> List[str]:
        """Find workers within radius of equipment"""
        
        if equipment_id not in self.assets:
            return []
        
        equipment_loc = self.assets[equipment_id].location
        
        nearby_workers = []
        
        for asset_id, asset in self.assets.items():
            if asset.asset_type != AssetType.WORKER:
                continue
            
            distance = self._calculate_distance(equipment_loc, asset.location)
            if distance <= radius_meters:
                nearby_workers.append(asset_id)
        
        return nearby_workers
    
    def _calculate_distance(
        self,
        loc1: Dict[str, float],
        loc2: Dict[str, float]
    ) -> float:
        """Calculate Euclidean distance between two locations"""
        
        dx = loc1.get('x', 0) - loc2.get('x', 0)
        dy = loc1.get('y', 0) - loc2.get('y', 0)
        dz = loc1.get('z', 0) - loc2.get('z', 0)
        
        return np.sqrt(dx**2 + dy**2 + dz**2)
    
    def _is_in_zone(self, location: Dict[str, float], zone: str) -> bool:
        """Check if location is within a zone"""
        # Simplified zone check
        return True  # In real system, would check zone boundaries
    
    def _estimate_downtime(self, failure_type: str) -> float:
        """Estimate downtime hours based on failure type"""
        
        downtime_estimates = {
            'sudden_stop': 2.0,
            'mechanical_failure': 4.0,
            'electrical_failure': 6.0,
            'fire': 24.0,
            'structural_damage': 48.0
        }
        
        return downtime_estimates.get(failure_type, 4.0)
    
    def _identify_evacuation_bottlenecks(
        self,
        workers: List[str],
        exit_points: int
    ) -> List[str]:
        """Identify evacuation bottlenecks"""
        
        bottlenecks = []
        
        workers_per_exit = len(workers) / max(1, exit_points)
        
        if workers_per_exit > 25:
            bottlenecks.append(f"Insufficient exits ({exit_points}) for {len(workers)} workers")
        
        return bottlenecks
    
    def _calculate_evacuation_risk(self, worker_id: str, zone: str) -> float:
        """Calculate evacuation risk for a worker"""
        
        # Simplified risk calculation
        return 0.5  # 50% base risk
    
    def _identify_capacity_bottlenecks(self, target_capacity: int) -> List[str]:
        """Identify capacity bottlenecks"""
        
        bottlenecks = []
        
        # Equipment capacity
        equipment_count = sum(
            1 for asset in self.assets.values()
            if asset.asset_type == AssetType.EQUIPMENT
        )
        
        required_equipment = target_capacity // 10  # 1 equipment per 10 workers
        
        if equipment_count < required_equipment:
            bottlenecks.append(f"Insufficient equipment ({equipment_count} vs {required_equipment} needed)")
        
        return bottlenecks
    
    def _assess_simulation_risks(self, outcomes: List[Dict[str, Any]]) -> Dict[str, float]:
        """Assess risks from simulation outcomes"""
        
        risks = {
            'safety_risk': 0.0,
            'operational_risk': 0.0,
            'financial_risk': 0.0
        }
        
        for outcome in outcomes:
            # Safety risk
            if 'affected_workers' in outcome and outcome['affected_workers'] > 0:
                risks['safety_risk'] = max(risks['safety_risk'], 0.7)
            
            if outcome.get('evacuation_required'):
                risks['safety_risk'] = 0.9
            
            # Operational risk
            if 'downtime_cost_per_hour' in outcome:
                risks['operational_risk'] = 0.6
            
            # Financial risk
            if 'estimated_damage_cost' in outcome:
                cost = outcome['estimated_damage_cost']
                risks['financial_risk'] = min(1.0, cost / 100000.0)
        
        return risks
    
    def _generate_simulation_recommendations(
        self,
        outcomes: List[Dict[str, Any]],
        risks: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations from simulation"""
        
        recommendations = []
        
        # High safety risk
        if risks['safety_risk'] > 0.7:
            recommendations.append("Implement additional safety controls before proceeding")
            recommendations.append("Conduct safety briefing with all affected personnel")
        
        # High operational risk
        if risks['operational_risk'] > 0.5:
            recommendations.append("Prepare contingency plans for operational disruptions")
            recommendations.append("Ensure backup equipment availability")
        
        # High financial risk
        if risks['financial_risk'] > 0.6:
            recommendations.append("Review insurance coverage adequacy")
            recommendations.append("Consider risk mitigation investments")
        
        # Outcome-specific recommendations
        for outcome in outcomes:
            if outcome.get('bottlenecks'):
                recommendations.append(f"Address bottlenecks: {', '.join(outcome['bottlenecks'])}")
            
            if 'recommended_actions' in outcome:
                recommendations.extend(outcome['recommended_actions'])
        
        return list(set(recommendations))[:10]  # Unique, top 10
    
    def _calculate_simulation_confidence(
        self,
        current_state: Dict[str, Dict],
        parameters: Dict[str, Any]
    ) -> float:
        """Calculate confidence in simulation results"""
        
        # Base confidence
        confidence = 0.7
        
        # More synchronized assets = higher confidence
        sync_rate = self.sync_status['assets_in_sync'] / max(1, self.sync_status['total_assets'])
        confidence *= (0.5 + 0.5 * sync_rate)
        
        # More historical data = higher confidence
        avg_history_length = np.mean([
            len(history) for history in self.asset_history.values()
        ]) if self.asset_history else 0
        
        history_factor = min(1.0, avg_history_length / 100.0)
        confidence *= (0.7 + 0.3 * history_factor)
        
        return min(1.0, confidence)
    
    def generate_risk_heatmap(self, zone: str) -> Dict[str, Any]:
        """Generate risk heatmap for a zone"""
        
        # Get all assets in zone
        zone_assets = [
            asset for asset in self.assets.values()
            if self._is_in_zone(asset.location, zone)
        ]
        
        # Create grid
        grid_size = 10  # 10x10 grid
        heatmap = np.zeros((grid_size, grid_size))
        
        # Calculate risk for each grid cell
        for asset in zone_assets:
            # Simplified: place risk at asset location
            x_idx = int(asset.location.get('x', 0) % grid_size)
            y_idx = int(asset.location.get('y', 0) % grid_size)
            
            # Risk based on asset health
            risk_value = (100.0 - asset.health_score) / 100.0
            
            heatmap[y_idx, x_idx] += risk_value
        
        # Normalize
        if heatmap.max() > 0:
            heatmap = heatmap / heatmap.max()
        
        return {
            'zone': zone,
            'grid_size': grid_size,
            'heatmap': heatmap.tolist(),
            'max_risk': float(heatmap.max()),
            'avg_risk': float(heatmap.mean()),
            'high_risk_areas': self._identify_high_risk_areas(heatmap)
        }
    
    def _identify_high_risk_areas(self, heatmap: np.ndarray) -> List[Dict[str, Any]]:
        """Identify high-risk areas from heatmap"""
        
        threshold = 0.7
        high_risk = []
        
        for i in range(heatmap.shape[0]):
            for j in range(heatmap.shape[1]):
                if heatmap[i, j] > threshold:
                    high_risk.append({
                        'x': j,
                        'y': i,
                        'risk_level': float(heatmap[i, j])
                    })
        
        return high_risk
    
    def get_twin_analytics(self) -> Dict[str, Any]:
        """Get digital twin analytics"""
        
        return {
            'total_assets': len(self.assets),
            'assets_by_type': {
                asset_type.value: sum(
                    1 for a in self.assets.values() if a.asset_type == asset_type
                )
                for asset_type in AssetType
            },
            'average_health': np.mean([a.health_score for a in self.assets.values()]) if self.assets else 0.0,
            'sync_status': self.sync_status,
            'simulations_run': len(self.simulations),
            'historical_data_points': sum(len(h) for h in self.asset_history.values())
        }


# Global enhanced digital twin instance
enhanced_digital_twin = EnhancedDigitalTwin()
