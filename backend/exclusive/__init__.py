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

from .immune_system import safety_immune_system, SafetyImmuneSystem
from .root_cause_ai import root_cause_ai, RootCauseAI
from .environment_fusion import environment_fusion, EnvironmentFusion
from .behavioral_recognition import behavioral_recognition, BehavioralPatternRecognition
from .predictive_maintenance import predictive_maintenance, PredictiveMaintenance
from .fatigue_detection import advanced_fatigue_detection, AdvancedFatigueDetection
from .autonomous_response import enhanced_autonomous_response, EnhancedAutonomousResponse
from .digital_twin import enhanced_digital_twin, EnhancedDigitalTwin
from .compliance_drift import intelligent_compliance_drift, IntelligentComplianceDrift
from .intent_aware import enhanced_intent_aware_safety, EnhancedIntentAwareSafety

__all__ = [
    # Instances
    'safety_immune_system',
    'root_cause_ai',
    'environment_fusion',
    'behavioral_recognition',
    'predictive_maintenance',
    'advanced_fatigue_detection',
    'enhanced_autonomous_response',
    'enhanced_digital_twin',
    'intelligent_compliance_drift',
    'enhanced_intent_aware_safety',
    
    # Classes
    'SafetyImmuneSystem',
    'RootCauseAI',
    'EnvironmentFusion',
    'BehavioralPatternRecognition',
    'PredictiveMaintenance',
    'AdvancedFatigueDetection',
    'EnhancedAutonomousResponse',
    'EnhancedDigitalTwin',
    'IntelligentComplianceDrift',
    'EnhancedIntentAwareSafety',
]
