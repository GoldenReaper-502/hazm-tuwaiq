"""
HAZM TUWAIQ - Predictive Safety Module
ML-powered predictions, trend analysis, and proactive safety recommendations
"""

from .models import (
    Prediction, TrendAnalysis, RiskHeatmap, 
    SafetyTwin, ProactiveRecommendation
)
from .prediction_engine import PredictionEngine, get_prediction_engine
from .trend_analyzer import TrendAnalyzer, get_trend_analyzer
from .safety_twin import SafetyTwin as DigitalSafetyTwin, get_safety_twin
from .risk_mapper import RiskMapper, get_risk_mapper

__all__ = [
    'Prediction',
    'TrendAnalysis',
    'RiskHeatmap',
    'SafetyTwin',
    'ProactiveRecommendation',
    'PredictionEngine',
    'TrendAnalyzer',
    'DigitalSafetyTwin',
    'RiskMapper',
    'get_prediction_engine',
    'get_trend_analyzer',
    'get_safety_twin',
    'get_risk_mapper'
]
