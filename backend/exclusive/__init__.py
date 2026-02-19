"""
HAZM TUWAIQ - Exclusive Features Module

10 Revolutionary Safety Innovations:

1. Safety Immune System - Adaptive learning from incidents, builds "antibodies" against threats
2. Root Cause AI - Multi-method deep analysis (5 Whys, Fishbone, Barriers, Patterns)
3. Environment Fusion - Multi-sensor data fusion for holistic safety awareness
4. Behavioral Pattern Recognition - Deep behavioral analysis and risk prediction
5. Predictive Maintenance - AI-powered equipment failure prediction with ROI
6. Advanced Fatigue Detection - Multi-modal fatigue assessment (physiological + behavioral + environmental)
7. Enhanced Autonomous Response - Self-healing safety system with AI decision-making
8. Enhanced Digital Twin - Real-time digital replica with what-if simulation
9. Intelligent Compliance Drift - Detects normalization of deviance before violations
10. Enhanced Intent-Aware Safety - Advanced trajectory prediction and collision prevention

All systems are fully operational with self-learning capabilities.
"""

from .autonomous_response import (
    EnhancedAutonomousResponse,
    enhanced_autonomous_response,
)
from .behavioral_recognition import BehavioralPatternRecognition, behavioral_recognition
from .compliance_drift import IntelligentComplianceDrift, intelligent_compliance_drift
from .digital_twin import EnhancedDigitalTwin, enhanced_digital_twin
from .environment_fusion import EnvironmentFusion, environment_fusion
from .fatigue_detection import AdvancedFatigueDetection, advanced_fatigue_detection
from .immune_system import SafetyImmuneSystem, safety_immune_system
from .intent_aware import EnhancedIntentAwareSafety, enhanced_intent_aware_safety
from .predictive_maintenance import PredictiveMaintenance, predictive_maintenance
from .root_cause_ai import RootCauseAI, root_cause_ai

__all__ = [
    # Instances
    "safety_immune_system",
    "root_cause_ai",
    "environment_fusion",
    "behavioral_recognition",
    "predictive_maintenance",
    "advanced_fatigue_detection",
    "enhanced_autonomous_response",
    "enhanced_digital_twin",
    "intelligent_compliance_drift",
    "enhanced_intent_aware_safety",
    # Classes
    "SafetyImmuneSystem",
    "RootCauseAI",
    "EnvironmentFusion",
    "BehavioralPatternRecognition",
    "PredictiveMaintenance",
    "AdvancedFatigueDetection",
    "EnhancedAutonomousResponse",
    "EnhancedDigitalTwin",
    "IntelligentComplianceDrift",
    "EnhancedIntentAwareSafety",
]
