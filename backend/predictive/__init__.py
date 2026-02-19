"""
HAZM TUWAIQ - Predictive Safety Module
ML-powered predictions, trend analysis, and proactive safety recommendations
"""

from .models import (
    Prediction,
    ProactiveRecommendation,
    RiskHeatmap,
    SafetyTwin,
    TrendAnalysis,
)
from .prediction_engine import PredictionEngine, get_prediction_engine
from .risk_mapper import RiskMapper, get_risk_mapper
from .safety_twin import SafetyTwin as DigitalSafetyTwin
from .safety_twin import get_safety_twin
from .trend_analyzer import TrendAnalyzer, get_trend_analyzer

__all__ = [
    "Prediction",
    "TrendAnalysis",
    "RiskHeatmap",
    "SafetyTwin",
    "ProactiveRecommendation",
    "PredictionEngine",
    "TrendAnalyzer",
    "DigitalSafetyTwin",
    "RiskMapper",
    "get_prediction_engine",
    "get_trend_analyzer",
    "get_safety_twin",
    "get_risk_mapper",
]
