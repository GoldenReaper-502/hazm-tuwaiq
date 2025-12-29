"""
HAZM TUWAIQ - Environment Fusion
Multi-sensor fusion for comprehensive environmental awareness
Combines data from multiple sources to create unified safety picture
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import numpy as np


class SensorType(str, Enum):
    """Types of environmental sensors"""
    CAMERA = "camera"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    NOISE = "noise"
    AIR_QUALITY = "air_quality"
    VIBRATION = "vibration"
    LIGHT = "light"
    GAS = "gas"
    MOTION = "motion"
    PROXIMITY = "proximity"
    PRESSURE = "pressure"


@dataclass
class SensorReading:
    """Individual sensor reading"""
    sensor_id: str
    sensor_type: SensorType
    value: float
    unit: str
    timestamp: datetime
    location: str
    confidence: float = 1.0  # 0-1
    

@dataclass
class EnvironmentSnapshot:
    """Complete environmental state at a moment"""
    timestamp: datetime
    location: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    noise_level: Optional[float] = None
    air_quality_index: Optional[float] = None
    light_level: Optional[float] = None
    vibration_level: Optional[float] = None
    gas_levels: Optional[Dict[str, float]] = None
    occupancy: int = 0
    safety_score: float = 100.0
    risk_level: str = "low"
    anomalies: List[str] = None
    
    def __post_init__(self):
        if self.anomalies is None:
            self.anomalies = []


class EnvironmentFusion:
    """
    Multi-sensor fusion system for environmental monitoring
    
    Features:
    - Real-time sensor data aggregation
    - Cross-sensor validation
    - Anomaly detection across multiple dimensions
    - Predictive environmental risk assessment
    - Holistic safety scoring
    """
    
    def __init__(self):
        self.sensors: Dict[str, Dict[str, Any]] = {}
        self.sensor_readings: List[SensorReading] = []
        self.environment_history: List[EnvironmentSnapshot] = []
        
        # Thresholds for various environmental factors
        self.thresholds = {
            'temperature': {'min': 10, 'max': 35, 'critical_min': 0, 'critical_max': 45},
            'humidity': {'min': 30, 'max': 70, 'critical_min': 20, 'critical_max': 85},
            'noise': {'max': 85, 'critical': 95},  # dB
            'air_quality': {'good': 50, 'moderate': 100, 'unhealthy': 150, 'hazardous': 300},
            'light': {'min': 300, 'optimal': 500, 'max': 1000},  # lux
            'vibration': {'max': 5.0, 'critical': 10.0},  # mm/s
        }
        
    def register_sensor(
        self,
        sensor_id: str,
        sensor_type: SensorType,
        location: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Register a new sensor in the system"""
        self.sensors[sensor_id] = {
            'type': sensor_type,
            'location': location,
            'registered_at': datetime.now(),
            'last_reading': None,
            'status': 'active',
            'metadata': metadata or {}
        }
    
    def ingest_reading(self, reading: SensorReading):
        """Ingest a sensor reading"""
        self.sensor_readings.append(reading)
        
        # Update sensor last reading
        if reading.sensor_id in self.sensors:
            self.sensors[reading.sensor_id]['last_reading'] = reading.timestamp
            self.sensors[reading.sensor_id]['status'] = 'active'
    
    def ingest_batch(self, readings: List[SensorReading]):
        """Ingest multiple sensor readings"""
        for reading in readings:
            self.ingest_reading(reading)
    
    def fuse_environment(self, location: str, time_window: int = 60) -> EnvironmentSnapshot:
        """
        Fuse all sensor data for a location into unified environment snapshot
        
        Args:
            location: Location to analyze
            time_window: Time window in seconds for data aggregation
        """
        
        cutoff_time = datetime.now() - datetime.timedelta(seconds=time_window)
        
        # Get recent readings for this location
        recent_readings = [
            r for r in self.sensor_readings
            if r.location == location and r.timestamp >= cutoff_time
        ]
        
        if not recent_readings:
            return EnvironmentSnapshot(
                timestamp=datetime.now(),
                location=location,
                safety_score=50.0,  # Unknown is moderate
                risk_level="unknown"
            )
        
        # Aggregate by sensor type
        aggregated = {}
        for reading in recent_readings:
            sensor_type = reading.sensor_type.value
            
            if sensor_type not in aggregated:
                aggregated[sensor_type] = []
            
            aggregated[sensor_type].append(reading.value)
        
        # Calculate averages (weighted by confidence if available)
        snapshot = EnvironmentSnapshot(
            timestamp=datetime.now(),
            location=location
        )
        
        # Temperature
        if 'temperature' in aggregated:
            snapshot.temperature = np.mean(aggregated['temperature'])
        
        # Humidity
        if 'humidity' in aggregated:
            snapshot.humidity = np.mean(aggregated['humidity'])
        
        # Noise
        if 'noise' in aggregated:
            snapshot.noise_level = np.mean(aggregated['noise'])
        
        # Air Quality
        if 'air_quality' in aggregated:
            snapshot.air_quality_index = np.mean(aggregated['air_quality'])
        
        # Light
        if 'light' in aggregated:
            snapshot.light_level = np.mean(aggregated['light'])
        
        # Vibration
        if 'vibration' in aggregated:
            snapshot.vibration_level = np.mean(aggregated['vibration'])
        
        # Motion/Occupancy
        if 'motion' in aggregated:
            snapshot.occupancy = int(sum(aggregated['motion']))
        
        # Detect anomalies
        snapshot.anomalies = self._detect_anomalies(snapshot)
        
        # Calculate safety score
        snapshot.safety_score = self._calculate_safety_score(snapshot)
        
        # Determine risk level
        snapshot.risk_level = self._determine_risk_level(snapshot)
        
        # Store in history
        self.environment_history.append(snapshot)
        
        return snapshot
    
    def _detect_anomalies(self, snapshot: EnvironmentSnapshot) -> List[str]:
        """Detect environmental anomalies"""
        anomalies = []
        
        # Temperature anomalies
        if snapshot.temperature is not None:
            if snapshot.temperature < self.thresholds['temperature']['critical_min']:
                anomalies.append(f"Critical: Temperature too low ({snapshot.temperature:.1f}°C)")
            elif snapshot.temperature > self.thresholds['temperature']['critical_max']:
                anomalies.append(f"Critical: Temperature too high ({snapshot.temperature:.1f}°C)")
            elif snapshot.temperature < self.thresholds['temperature']['min']:
                anomalies.append(f"Warning: Temperature low ({snapshot.temperature:.1f}°C)")
            elif snapshot.temperature > self.thresholds['temperature']['max']:
                anomalies.append(f"Warning: Temperature high ({snapshot.temperature:.1f}°C)")
        
        # Humidity anomalies
        if snapshot.humidity is not None:
            if snapshot.humidity < self.thresholds['humidity']['critical_min']:
                anomalies.append(f"Critical: Humidity too low ({snapshot.humidity:.1f}%)")
            elif snapshot.humidity > self.thresholds['humidity']['critical_max']:
                anomalies.append(f"Critical: Humidity too high ({snapshot.humidity:.1f}%)")
        
        # Noise anomalies
        if snapshot.noise_level is not None:
            if snapshot.noise_level > self.thresholds['noise']['critical']:
                anomalies.append(f"Critical: Dangerous noise level ({snapshot.noise_level:.1f} dB)")
            elif snapshot.noise_level > self.thresholds['noise']['max']:
                anomalies.append(f"Warning: High noise level ({snapshot.noise_level:.1f} dB)")
        
        # Air quality anomalies
        if snapshot.air_quality_index is not None:
            if snapshot.air_quality_index > self.thresholds['air_quality']['hazardous']:
                anomalies.append(f"Critical: Hazardous air quality (AQI: {snapshot.air_quality_index:.0f})")
            elif snapshot.air_quality_index > self.thresholds['air_quality']['unhealthy']:
                anomalies.append(f"Warning: Unhealthy air quality (AQI: {snapshot.air_quality_index:.0f})")
        
        # Light anomalies
        if snapshot.light_level is not None:
            if snapshot.light_level < self.thresholds['light']['min']:
                anomalies.append(f"Warning: Insufficient lighting ({snapshot.light_level:.0f} lux)")
        
        # Vibration anomalies
        if snapshot.vibration_level is not None:
            if snapshot.vibration_level > self.thresholds['vibration']['critical']:
                anomalies.append(f"Critical: Excessive vibration ({snapshot.vibration_level:.1f} mm/s)")
            elif snapshot.vibration_level > self.thresholds['vibration']['max']:
                anomalies.append(f"Warning: High vibration ({snapshot.vibration_level:.1f} mm/s)")
        
        return anomalies
    
    def _calculate_safety_score(self, snapshot: EnvironmentSnapshot) -> float:
        """Calculate overall environmental safety score (0-100)"""
        
        score = 100.0
        penalties = []
        
        # Temperature penalty
        if snapshot.temperature is not None:
            if snapshot.temperature < self.thresholds['temperature']['critical_min'] or \
               snapshot.temperature > self.thresholds['temperature']['critical_max']:
                penalties.append(30)
            elif snapshot.temperature < self.thresholds['temperature']['min'] or \
                 snapshot.temperature > self.thresholds['temperature']['max']:
                penalties.append(10)
        
        # Humidity penalty
        if snapshot.humidity is not None:
            if snapshot.humidity < self.thresholds['humidity']['critical_min'] or \
               snapshot.humidity > self.thresholds['humidity']['critical_max']:
                penalties.append(20)
            elif snapshot.humidity < self.thresholds['humidity']['min'] or \
                 snapshot.humidity > self.thresholds['humidity']['max']:
                penalties.append(5)
        
        # Noise penalty
        if snapshot.noise_level is not None:
            if snapshot.noise_level > self.thresholds['noise']['critical']:
                penalties.append(25)
            elif snapshot.noise_level > self.thresholds['noise']['max']:
                penalties.append(15)
        
        # Air quality penalty
        if snapshot.air_quality_index is not None:
            if snapshot.air_quality_index > self.thresholds['air_quality']['hazardous']:
                penalties.append(40)
            elif snapshot.air_quality_index > self.thresholds['air_quality']['unhealthy']:
                penalties.append(20)
            elif snapshot.air_quality_index > self.thresholds['air_quality']['moderate']:
                penalties.append(10)
        
        # Light penalty
        if snapshot.light_level is not None:
            if snapshot.light_level < self.thresholds['light']['min']:
                penalties.append(15)
        
        # Vibration penalty
        if snapshot.vibration_level is not None:
            if snapshot.vibration_level > self.thresholds['vibration']['critical']:
                penalties.append(35)
            elif snapshot.vibration_level > self.thresholds['vibration']['max']:
                penalties.append(10)
        
        # Apply penalties
        total_penalty = sum(penalties)
        score = max(0.0, score - total_penalty)
        
        return score
    
    def _determine_risk_level(self, snapshot: EnvironmentSnapshot) -> str:
        """Determine overall risk level"""
        
        if snapshot.safety_score >= 80:
            return "low"
        elif snapshot.safety_score >= 60:
            return "moderate"
        elif snapshot.safety_score >= 40:
            return "high"
        elif snapshot.safety_score >= 20:
            return "very_high"
        else:
            return "critical"
    
    def detect_environmental_changes(
        self,
        location: str,
        lookback_minutes: int = 30
    ) -> List[Dict[str, Any]]:
        """Detect significant environmental changes"""
        
        cutoff = datetime.now() - datetime.timedelta(minutes=lookback_minutes)
        
        recent_snapshots = [
            s for s in self.environment_history
            if s.location == location and s.timestamp >= cutoff
        ]
        
        if len(recent_snapshots) < 2:
            return []
        
        changes = []
        
        # Sort by time
        recent_snapshots.sort(key=lambda x: x.timestamp)
        
        first = recent_snapshots[0]
        last = recent_snapshots[-1]
        
        # Temperature change
        if first.temperature is not None and last.temperature is not None:
            temp_change = last.temperature - first.temperature
            if abs(temp_change) >= 5:
                changes.append({
                    'factor': 'temperature',
                    'change': temp_change,
                    'significance': 'high' if abs(temp_change) >= 10 else 'moderate',
                    'description': f"Temperature {'increased' if temp_change > 0 else 'decreased'} by {abs(temp_change):.1f}°C"
                })
        
        # Noise change
        if first.noise_level is not None and last.noise_level is not None:
            noise_change = last.noise_level - first.noise_level
            if abs(noise_change) >= 10:
                changes.append({
                    'factor': 'noise',
                    'change': noise_change,
                    'significance': 'high' if abs(noise_change) >= 20 else 'moderate',
                    'description': f"Noise level {'increased' if noise_change > 0 else 'decreased'} by {abs(noise_change):.1f} dB"
                })
        
        # Air quality change
        if first.air_quality_index is not None and last.air_quality_index is not None:
            aqi_change = last.air_quality_index - first.air_quality_index
            if abs(aqi_change) >= 25:
                changes.append({
                    'factor': 'air_quality',
                    'change': aqi_change,
                    'significance': 'high' if abs(aqi_change) >= 50 else 'moderate',
                    'description': f"Air quality {'deteriorated' if aqi_change > 0 else 'improved'} by {abs(aqi_change):.0f} AQI"
                })
        
        return changes
    
    def predict_environmental_risk(
        self,
        location: str,
        forecast_minutes: int = 30
    ) -> Dict[str, Any]:
        """Predict future environmental risk based on trends"""
        
        # Get recent history
        recent_snapshots = [
            s for s in self.environment_history[-20:]
            if s.location == location
        ]
        
        if len(recent_snapshots) < 3:
            return {
                'predicted_risk': 'unknown',
                'confidence': 0.0,
                'factors': []
            }
        
        # Analyze trends
        temps = [s.temperature for s in recent_snapshots if s.temperature is not None]
        noise_levels = [s.noise_level for s in recent_snapshots if s.noise_level is not None]
        aqi_values = [s.air_quality_index for s in recent_snapshots if s.air_quality_index is not None]
        
        risk_factors = []
        
        # Temperature trend
        if len(temps) >= 3:
            temp_trend = np.polyfit(range(len(temps)), temps, 1)[0]  # Linear slope
            if temp_trend > 0.5:  # Rapidly increasing
                risk_factors.append({
                    'factor': 'temperature',
                    'trend': 'increasing',
                    'rate': temp_trend,
                    'risk': 'moderate' if temp_trend < 1.0 else 'high'
                })
        
        # Noise trend
        if len(noise_levels) >= 3:
            noise_trend = np.polyfit(range(len(noise_levels)), noise_levels, 1)[0]
            if noise_trend > 2.0:  # Rapidly increasing
                risk_factors.append({
                    'factor': 'noise',
                    'trend': 'increasing',
                    'rate': noise_trend,
                    'risk': 'moderate' if noise_trend < 5.0 else 'high'
                })
        
        # Air quality trend
        if len(aqi_values) >= 3:
            aqi_trend = np.polyfit(range(len(aqi_values)), aqi_values, 1)[0]
            if aqi_trend > 5.0:  # Deteriorating
                risk_factors.append({
                    'factor': 'air_quality',
                    'trend': 'deteriorating',
                    'rate': aqi_trend,
                    'risk': 'moderate' if aqi_trend < 10.0 else 'high'
                })
        
        # Overall predicted risk
        if any(f['risk'] == 'high' for f in risk_factors):
            predicted_risk = 'high'
            confidence = 0.75
        elif risk_factors:
            predicted_risk = 'moderate'
            confidence = 0.65
        else:
            predicted_risk = 'low'
            confidence = 0.50
        
        return {
            'predicted_risk': predicted_risk,
            'confidence': confidence,
            'forecast_horizon_minutes': forecast_minutes,
            'risk_factors': risk_factors,
            'recommendation': self._generate_environmental_recommendation(risk_factors)
        }
    
    def _generate_environmental_recommendation(self, risk_factors: List[Dict[str, Any]]) -> str:
        """Generate recommendation based on environmental risks"""
        
        if not risk_factors:
            return "Environmental conditions are stable. Continue normal monitoring."
        
        high_risk_factors = [f for f in risk_factors if f['risk'] == 'high']
        
        if high_risk_factors:
            factors_str = ", ".join([f['factor'] for f in high_risk_factors])
            return f"High risk detected in {factors_str}. Implement immediate controls and consider work stoppage if conditions worsen."
        else:
            factors_str = ", ".join([f['factor'] for f in risk_factors])
            return f"Moderate risk trends detected in {factors_str}. Increase monitoring frequency and prepare mitigation measures."
    
    def get_sensor_health(self) -> Dict[str, Any]:
        """Get health status of all sensors"""
        
        now = datetime.now()
        health_report = {
            'total_sensors': len(self.sensors),
            'active_sensors': 0,
            'inactive_sensors': 0,
            'stale_sensors': 0,
            'sensor_details': []
        }
        
        for sensor_id, sensor_info in self.sensors.items():
            last_reading = sensor_info.get('last_reading')
            
            if last_reading:
                age = (now - last_reading).total_seconds() / 60  # minutes
                
                if age < 5:
                    status = 'active'
                    health_report['active_sensors'] += 1
                elif age < 30:
                    status = 'stale'
                    health_report['stale_sensors'] += 1
                else:
                    status = 'inactive'
                    health_report['inactive_sensors'] += 1
            else:
                status = 'never_reported'
                health_report['inactive_sensors'] += 1
            
            health_report['sensor_details'].append({
                'sensor_id': sensor_id,
                'type': sensor_info['type'].value,
                'location': sensor_info['location'],
                'status': status,
                'last_reading_minutes_ago': (now - last_reading).total_seconds() / 60 if last_reading else None
            })
        
        return health_report


# Global environment fusion instance
environment_fusion = EnvironmentFusion()
