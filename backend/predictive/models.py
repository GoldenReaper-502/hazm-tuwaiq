"""
HAZM TUWAIQ - Predictive Safety Models
Data models for predictions, trends, and risk analysis
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# ═══════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════

class PredictionType(str, Enum):
    """نوع التنبؤ"""
    INCIDENT_PROBABILITY = "incident_probability"
    NEAR_MISS_FORECAST = "near_miss_forecast"
    RISK_SCORE = "risk_score"
    FATIGUE_PATTERN = "fatigue_pattern"
    EQUIPMENT_FAILURE = "equipment_failure"
    COMPLIANCE_DRIFT = "compliance_drift"
    BEHAVIOR_CHANGE = "behavior_change"


class RiskLevel(str, Enum):
    """مستوى الخطر"""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"


class TrendDirection(str, Enum):
    """اتجاه الاتجاه"""
    IMPROVING = "improving"       # تحسن
    STABLE = "stable"              # مستقر
    DEGRADING = "degrading"        # تدهور
    VOLATILE = "volatile"          # متقلب


class TimeFrame(str, Enum):
    """الإطار الزمني"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


# ═══════════════════════════════════════════════════════════
# CORE MODELS
# ═══════════════════════════════════════════════════════════

class Prediction(BaseModel):
    """
    التنبؤ - Prediction
    ML-powered safety prediction
    """
    id: str = Field(default_factory=lambda: f"PRED-{uuid.uuid4().hex[:12].upper()}")
    
    # Type & Target
    type: PredictionType
    target: str  # Zone, Camera, Worker, Equipment
    
    # Prediction
    probability: float = Field(ge=0, le=1)  # 0-1
    risk_level: RiskLevel
    confidence: float = Field(ge=0, le=1)
    
    # Timeframe
    forecast_period: str  # e.g., "next_24h", "next_week"
    valid_from: datetime = Field(default_factory=datetime.now)
    valid_until: datetime
    
    # Details
    title: str
    title_ar: Optional[str] = None
    description: str
    description_ar: Optional[str] = None
    
    # Contributing Factors
    factors: List[Dict[str, Any]] = Field(default_factory=list)
    # Example: [{"factor": "high_fatigue_incidents", "weight": 0.3, "trend": "increasing"}]
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list)
    
    # Model Info
    model_name: str = "SafetyPredictor-v1"
    model_version: str = "1.0.0"
    
    # Metadata
    organization_id: str
    site_id: Optional[str] = None
    zone: Optional[str] = None
    
    # Tracking
    created_at: datetime = Field(default_factory=datetime.now)
    accuracy_score: Optional[float] = None  # Filled after validation
    was_accurate: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "incident_probability",
                "target": "Zone-A",
                "probability": 0.78,
                "risk_level": "high",
                "confidence": 0.85,
                "forecast_period": "next_24h",
                "title": "High incident probability in Zone A",
                "factors": [
                    {"factor": "increased_fatigue", "weight": 0.4},
                    {"factor": "equipment_aging", "weight": 0.3}
                ]
            }
        }


class TrendAnalysis(BaseModel):
    """
    تحليل الاتجاه - Trend Analysis
    Historical trend analysis with pattern detection
    """
    id: str = Field(default_factory=lambda: f"TREND-{uuid.uuid4().hex[:12].upper()}")
    
    # Analysis Target
    metric: str  # e.g., "incident_rate", "near_miss_count", "compliance_score"
    metric_ar: Optional[str] = None
    target: str  # Zone, Site, Organization
    
    # Time Period
    time_frame: TimeFrame
    start_date: datetime
    end_date: datetime
    data_points: int
    
    # Trend Results
    direction: TrendDirection
    change_percentage: float  # -100 to +100
    slope: float  # Rate of change
    
    # Statistical Analysis
    mean: float
    median: float
    std_deviation: float
    min_value: float
    max_value: float
    
    # Pattern Detection
    patterns_detected: List[str] = Field(default_factory=list)
    # Examples: ["weekly_spike", "morning_peak", "weekend_drop"]
    
    seasonality: Optional[Dict[str, Any]] = None
    # Example: {"pattern": "weekly", "peak_day": "Monday", "strength": 0.7}
    
    anomalies: List[Dict[str, Any]] = Field(default_factory=list)
    # Example: [{"date": "2024-01-15", "value": 25, "expected": 10, "deviation": 2.5}]
    
    # Visualization Data
    time_series: List[Dict[str, Any]] = Field(default_factory=list)
    # Example: [{"timestamp": "2024-01-01T00:00:00", "value": 12}]
    
    # Interpretation
    summary: str
    summary_ar: Optional[str] = None
    insights: List[str] = Field(default_factory=list)
    
    # Metadata
    organization_id: str
    created_at: datetime = Field(default_factory=datetime.now)


class RiskHeatmap(BaseModel):
    """
    خريطة المخاطر - Risk Heatmap
    Spatial risk distribution across site/zones
    """
    id: str = Field(default_factory=lambda: f"HMAP-{uuid.uuid4().hex[:12].upper()}")
    
    # Scope
    site_id: str
    time_period: str  # e.g., "last_7_days", "current_shift"
    
    # Risk Data by Zone
    zones: List[Dict[str, Any]] = Field(default_factory=list)
    # Example: [
    #   {
    #     "zone_id": "ZONE-A",
    #     "zone_name": "Welding Area",
    #     "risk_score": 0.85,
    #     "risk_level": "high",
    #     "incident_count": 5,
    #     "near_miss_count": 12,
    #     "coordinates": {"x": 100, "y": 200, "radius": 50}
    #   }
    # ]
    
    # Aggregate Statistics
    total_zones: int
    highest_risk_zone: str
    lowest_risk_zone: str
    average_risk_score: float
    
    # Risk Distribution
    risk_distribution: Dict[str, int] = Field(default_factory=dict)
    # Example: {"critical": 2, "high": 5, "moderate": 8, "low": 10}
    
    # Hot Spots (areas requiring immediate attention)
    hot_spots: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Visualization Config
    color_mapping: Dict[str, str] = Field(default_factory=lambda: {
        "very_low": "#22c55e",
        "low": "#84cc16",
        "moderate": "#eab308",
        "high": "#f97316",
        "very_high": "#ef4444",
        "critical": "#dc2626"
    })
    
    # Metadata
    organization_id: str
    generated_at: datetime = Field(default_factory=datetime.now)


class SafetyTwin(BaseModel):
    """
    التوأم الرقمي للسلامة - Digital Safety Twin
    Real-time virtual representation of safety state
    """
    id: str = Field(default_factory=lambda: f"TWIN-{uuid.uuid4().hex[:12].upper()}")
    
    # Twin Identity
    twin_type: str  # "site", "zone", "worker", "equipment"
    twin_name: str
    real_entity_id: str
    
    # Current State
    safety_score: float = Field(ge=0, le=100)  # 0-100
    health_status: str  # "healthy", "warning", "critical"
    
    # Real-time Metrics
    active_workers: int = 0
    active_equipment: int = 0
    active_alerts: int = 0
    compliance_rate: float = 0.0  # 0-100%
    
    # Environmental Conditions
    environment: Dict[str, Any] = Field(default_factory=dict)
    # Example: {"temperature": 28, "humidity": 65, "noise_level": 75}
    
    # Historical Performance
    incidents_24h: int = 0
    near_misses_24h: int = 0
    safety_violations_24h: int = 0
    
    # Predictive Insights
    predicted_risk_level: RiskLevel = RiskLevel.LOW
    risk_trend: TrendDirection = TrendDirection.STABLE
    next_incident_probability: float = 0.0
    
    # Anomalies
    current_anomalies: List[str] = Field(default_factory=list)
    
    # Recommendations
    active_recommendations: List[str] = Field(default_factory=list)
    
    # Simulation Results
    what_if_scenarios: List[Dict[str, Any]] = Field(default_factory=list)
    # Example: [
    #   {
    #     "scenario": "increase_supervision",
    #     "expected_risk_reduction": 0.25,
    #     "cost": "medium"
    #   }
    # ]
    
    # Metadata
    organization_id: str
    last_updated: datetime = Field(default_factory=datetime.now)
    sync_status: str = "synchronized"  # "synchronized", "out_of_sync", "error"


class ProactiveRecommendation(BaseModel):
    """
    التوصية الاستباقية - Proactive Recommendation
    AI-generated safety recommendations
    """
    id: str = Field(default_factory=lambda: f"REC-{uuid.uuid4().hex[:12].upper()}")
    
    # Recommendation Details
    title: str
    title_ar: Optional[str] = None
    description: str
    description_ar: Optional[str] = None
    
    # Priority & Impact
    priority: str = "medium"  # "low", "medium", "high", "urgent"
    expected_impact: float = Field(ge=0, le=1)  # 0-1 (risk reduction)
    confidence: float = Field(ge=0, le=1)
    
    # Category
    category: str  # "training", "equipment", "process", "supervision"
    category_ar: Optional[str] = None
    
    # Target
    applies_to: str  # Zone, Worker, Equipment
    organization_id: str
    site_id: Optional[str] = None
    
    # Rationale
    reasoning: List[str] = Field(default_factory=list)
    supporting_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Implementation
    action_steps: List[str] = Field(default_factory=list)
    estimated_cost: Optional[str] = None  # "low", "medium", "high"
    estimated_duration: Optional[str] = None  # e.g., "2 weeks"
    
    # Status
    status: str = "pending"  # "pending", "accepted", "in_progress", "completed", "rejected"
    accepted_by: Optional[str] = None
    accepted_at: Optional[datetime] = None
    
    # Effectiveness Tracking
    implemented_at: Optional[datetime] = None
    effectiveness_score: Optional[float] = None  # Measured after implementation
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Increase supervision during peak hours",
                "title_ar": "زيادة الإشراف خلال ساعات الذروة",
                "priority": "high",
                "expected_impact": 0.4,
                "confidence": 0.82,
                "category": "supervision",
                "reasoning": [
                    "80% of incidents occur during morning shift",
                    "Supervision ratio currently 1:15, recommended 1:10"
                ],
                "action_steps": [
                    "Assign 2 additional supervisors for morning shift",
                    "Implement mobile patrol schedule"
                ]
            }
        }


# ═══════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════

class PredictionRequest(BaseModel):
    """طلب تنبؤ"""
    prediction_type: PredictionType
    target: str
    forecast_period: str
    organization_id: str
    site_id: Optional[str] = None
    include_recommendations: bool = True


class TrendAnalysisRequest(BaseModel):
    """طلب تحليل اتجاه"""
    metric: str
    target: str
    time_frame: TimeFrame
    days_back: int = 30
    organization_id: str


class RiskHeatmapRequest(BaseModel):
    """طلب خريطة مخاطر"""
    site_id: str
    time_period: str = "last_7_days"
    organization_id: str
    min_risk_threshold: Optional[float] = None


class SafetyTwinUpdate(BaseModel):
    """تحديث التوأم الرقمي"""
    twin_id: str
    metrics: Dict[str, Any]
    environment: Optional[Dict[str, Any]] = None
