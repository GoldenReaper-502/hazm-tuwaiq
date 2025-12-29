"""
🌌 HAZM TUWAIQ - Sovereignty API Router
========================================

Sovereign Endpoints:
/sense    - الاستشعار السياقي
/decide   - القرار السيادي
/act      - التنفيذ الذاتي
/explain  - التفسير الكامل
/audit    - المحاسبة
/forecast - التنبؤ بالمستقبل
/govern   - الحوكمة
"""

from fastapi import APIRouter, Body, HTTPException, Query
from typing import Dict, Any, Optional, List
from datetime import datetime

from .sovereignty_engine import (
    sovereignty_engine,
    ContextualAwareness,
    SovereignDecision,
    ConsciousnessLevel,
    DangerLevel,
    InterventionLevel
)

router = APIRouter()


# ═══════════════════════════════════════════════════════════
# SOVEREIGN ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/sovereignty/overview")
def sovereignty_overview():
    """نظرة عامة على النظام السيادي"""
    return {
        "system": "HAZM TUWAIQ - Sovereignty Engine",
        "philosophy": "ليس منصة... بل ظاهرة",
        "tagline": "Before HAZM TUWAIQ ≠ After HAZM TUWAIQ",
        
        "consciousness": {
            "current_level": sovereignty_engine.consciousness_level.name,
            "capabilities": [
                "Contextual Awareness",
                "Autonomous Decision Making",
                "Self-Intervention",
                "Complete Explanation",
                "Accountability",
                "Future Forecasting",
                "Governance Intelligence"
            ]
        },
        
        "endpoints": {
            "/sense": "Contextual sensing - ما يحدث الآن؟",
            "/decide": "Sovereign decision - ما يجب فعله؟",
            "/act": "Autonomous action - تنفيذ فوري",
            "/explain": "Complete explanation - لماذا؟",
            "/audit": "Accountability - من فعل ماذا؟",
            "/forecast": "Future prediction - ماذا سيحدث؟",
            "/govern": "Governance - من يملك القرار؟"
        },
        
        "principles": {
            "zero_trust": "كل قرار له سبب",
            "json_only": "كل شيء بيانات",
            "no_silent_errors": "كل خطأ له صوت",
            "constitutional": "قوانين لا تُتجاوز",
            "explainable": "شفافية كاملة"
        },
        
        "metrics": {
            "total_decisions": len(sovereignty_engine.decision_history),
            "contextual_memories": len(sovereignty_engine.contextual_memory)
        }
    }


@router.post("/sense")
def sense(inputs: Dict[str, Any] = Body(...)):
    """
    🔍 SENSE - الاستشعار السياقي
    
    ليس فقط "ما يحدث"... بل السياق الكامل
    """
    try:
        awareness = sovereignty_engine.sense(inputs)
        
        return {
            "status": "SENSING_COMPLETE",
            "consciousness_level": awareness.consciousness_level.name,
            "confidence": awareness.confidence,
            
            "now": {
                "current_state": awareness.current_state,
                "active_risks": awareness.active_risks,
                "ongoing_activities": awareness.ongoing_activities
            },
            
            "soon": {
                "predicted_risks": awareness.predicted_risks,
                "trends": awareness.trend_analysis
            },
            
            "before": {
                "historical_patterns": awareness.historical_patterns,
                "learned_behaviors": awareness.learned_behaviors
            },
            
            "context": {
                "environment": awareness.environmental_factors,
                "organization": awareness.organizational_context
            },
            
            "timestamp": awareness.timestamp.isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/decide")
def decide(
    inputs: Dict[str, Any] = Body(...),
    constitution_rules: Optional[List[Dict]] = Body(None)
):
    """
    ⚖️ DECIDE - القرار السيادي
    
    قرار مبني على وعي كامل، مُبرر، قابل للمحاسبة
    """
    try:
        # أولاً: استشعار
        awareness = sovereignty_engine.sense(inputs)
        
        # ثانياً: قرار
        decision = sovereignty_engine.decide(awareness, constitution_rules)
        
        return {
            "status": "DECISION_MADE",
            "decision_id": decision.decision_id,
            "decision": decision.decision,
            
            "reasoning": {
                "why": decision.reasoning,
                "confidence": f"{decision.confidence * 100:.1f}%",
                "data_sources": decision.data_sources
            },
            
            "alternatives": {
                "total_considered": len(decision.alternatives_considered),
                "alternatives": decision.alternatives_considered
            },
            
            "risk": decision.risk_assessment,
            
            "authority": {
                "level": decision.authority_level,
                "requires_human": decision.requires_human_approval,
                "decision_maker": decision.decision_maker
            },
            
            "intervention": {
                "level": decision.intervention_level.name,
                "actions": decision.actions
            },
            
            "timestamp": decision.timestamp.isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/act")
def act(decision_id: str = Body(..., embed=True)):
    """
    ⚡ ACT - التنفيذ الذاتي
    
    النظام لا يقترح فقط... بل يتدخل
    """
    try:
        # البحث عن القرار
        decision = sovereignty_engine._find_decision(decision_id)
        
        if not decision:
            raise HTTPException(status_code=404, detail="Decision not found")
        
        # التنفيذ
        result = sovereignty_engine.act(decision)
        
        return {
            "status": result["status"],
            "decision_id": decision_id,
            "execution": result,
            "principle": "القرار أولاً، المحاسبة ثانياً، السلامة دائماً"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/explain/{decision_id}")
def explain(decision_id: str):
    """
    💡 EXPLAIN - التفسير الكامل
    
    لماذا اتخذ النظام هذا القرار؟
    شفافية 100%
    """
    try:
        explanation = sovereignty_engine.explain(decision_id)
        
        if "error" in explanation:
            raise HTTPException(status_code=404, detail=explanation["error"])
        
        return {
            "status": "EXPLANATION_READY",
            "explanation": explanation,
            "transparency_score": 1.0,
            "principle": "كل قرار له سبب، وكل سبب له سجل"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit")
def audit(
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    filter_type: Optional[str] = Query(None)
):
    """
    📋 AUDIT - المحاسبة
    
    من فعل ماذا ومتى ولماذا؟
    سجل لا يُزوّر، درع قانوني
    """
    try:
        start_dt = datetime.fromisoformat(start_time) if start_time else None
        end_dt = datetime.fromisoformat(end_time) if end_time else None
        filters = {"type": filter_type} if filter_type else None
        
        audit_report = sovereignty_engine.audit(start_dt, end_dt, filters)
        
        return {
            "status": "AUDIT_COMPLETE",
            "report": audit_report,
            "legal_shield": audit_report.get("legal_shield", {}),
            "principle": "السلامة = درع قانوني"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast")
def forecast(
    inputs: Dict[str, Any] = Body(...),
    time_horizon: int = Body(1800)  # 30 minutes default
):
    """
    🔮 FORECAST - التنبؤ بالمستقبل
    
    ماذا سيحدث؟ ماذا لو؟
    Shadow Reality - عالم موازٍ
    """
    try:
        # استشعار
        awareness = sovereignty_engine.sense(inputs)
        
        # تنبؤ
        forecast_result = sovereignty_engine.forecast(awareness, time_horizon)
        
        return {
            "status": "FORECAST_READY",
            "forecast": forecast_result,
            "shadow_reality": forecast_result.get("shadow_reality"),
            "principle": "رؤية الخطر قبل تكوّنه"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/govern")
def govern(query: Dict[str, Any] = Body(...)):
    """
    👑 GOVERN - الحوكمة
    
    من يملك القرار؟ من يتأثر؟ من يُحاسب؟
    Organization as a Graph
    """
    try:
        governance_response = sovereignty_engine.govern(query)
        
        return {
            "status": "GOVERNANCE_QUERY_RESOLVED",
            "response": governance_response,
            "principle": "المؤسسة = كائن حي"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# CONSCIOUSNESS ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/consciousness")
def get_consciousness_status():
    """حالة الوعي الحالية للنظام"""
    return {
        "consciousness_level": sovereignty_engine.consciousness_level.name,
        "description": _get_consciousness_description(
            sovereignty_engine.consciousness_level
        ),
        "capabilities_active": _get_active_capabilities(
            sovereignty_engine.consciousness_level
        ),
        "metrics": {
            "total_memories": len(sovereignty_engine.contextual_memory),
            "total_decisions": len(sovereignty_engine.decision_history),
            "learning_database_size": len(sovereignty_engine.learning_database)
        }
    }


def _get_consciousness_description(level: ConsciousnessLevel) -> str:
    """وصف مستوى الوعي"""
    descriptions = {
        ConsciousnessLevel.DORMANT: "النظام في وضع السكون",
        ConsciousnessLevel.SENSING: "النظام يستشعر البيئة",
        ConsciousnessLevel.AWARE: "النظام واعٍ بالمخاطر",
        ConsciousnessLevel.DECIDING: "النظام يتخذ قراراً",
        ConsciousnessLevel.ACTING: "النظام يتدخل",
        ConsciousnessLevel.LEARNING: "النظام يتعلم"
    }
    return descriptions.get(level, "Unknown")


def _get_active_capabilities(level: ConsciousnessLevel) -> List[str]:
    """القدرات النشطة حسب مستوى الوعي"""
    base_capabilities = ["sensing", "memory"]
    
    if level.value >= ConsciousnessLevel.AWARE.value:
        base_capabilities.append("risk_detection")
    
    if level.value >= ConsciousnessLevel.DECIDING.value:
        base_capabilities.extend(["decision_making", "reasoning"])
    
    if level.value >= ConsciousnessLevel.ACTING.value:
        base_capabilities.extend(["intervention", "execution"])
    
    if level.value >= ConsciousnessLevel.LEARNING.value:
        base_capabilities.extend(["learning", "adaptation"])
    
    return base_capabilities


# ═══════════════════════════════════════════════════════════
# PHENOMENON ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/phenomenon")
def get_phenomenon_status():
    """
    🌌 حالة الظاهرة
    
    ليس منصة... بل ظاهرة تغيّر مفهوم السلامة
    """
    return {
        "name": "HAZM TUWAIQ",
        "tagline": "Before HAZM TUWAIQ ≠ After HAZM TUWAIQ",
        "philosophy": "السلامة ليست امتثالاً... بل وعي سياقي",
        
        "paradigm_shift": {
            "before": {
                "safety": "تقارير PDF",
                "decision": "اجتماعات",
                "compliance": "أوراق",
                "risk": "يُكتشف متأخراً"
            },
            "after": {
                "safety": "قرار آني ذاتي",
                "decision": "AI + Human Synergy",
                "compliance": "تلقائي",
                "risk": "يُرصد قبل تكوّنه"
            }
        },
        
        "core_principles": {
            "consciousness": "وعي سياقي كامل",
            "sovereignty": "قرارات سيادية",
            "autonomy": "تدخل ذاتي",
            "explainability": "شفافية 100%",
            "accountability": "محاسبة كاملة",
            "constitution": "قوانين لا تُتجاوز"
        },
        
        "exclusive_powers": [
            "Zero-Typing Safety",
            "Safety Singularity Index",
            "AI Safety Copilot",
            "Shadow Reality Simulation",
            "Liability Shield",
            "Human-AI Authority Balance"
        ],
        
        "impact": {
            "thesis": "ما قبل حزم طويق ≠ ما بعد حزم طويق",
            "promise": "كل عامل يعود لأسرته سالماً",
            "mission": "صفر حوادث في 2030"
        }
    }


__all__ = ["router"]
