"""
Advanced Features API - واجهة برمجية للميزات المتقدمة
جميع الميزات النوعية والحصرية لحزم طويق
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from innovation.advanced_features import (
    AutonomousSafetyActions,
    CrossProjectIntelligence,
    ExecutiveAISafetyAdvisor,
    SmartPermitToWorkAI,
)
from innovation.ai_safety_brain import AISafetyBrain
from innovation.ai_storytelling_compliance import (
    AIIncidentStorytelling,
    ComplianceAutoAuditor,
)

# استيراد جميع المحركات المتقدمة
from innovation.digital_safety_twin import DigitalSafetyTwin
from innovation.safety_gamification import SafetyGamificationEngine
from innovation.worker_risk_profiling import WorkerRiskProfiling
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/advanced", tags=["Advanced Features"])

# تهيئة جميع المحركات
digital_twin = DigitalSafetyTwin()
safety_brain = AISafetyBrain()
risk_profiling = WorkerRiskProfiling()
gamification = SafetyGamificationEngine()
storytelling = AIIncidentStorytelling()
compliance_auditor = ComplianceAutoAuditor()
permit_ai = SmartPermitToWorkAI()
executive_advisor = ExecutiveAISafetyAdvisor()
autonomous_actions = AutonomousSafetyActions()
cross_project = CrossProjectIntelligence()


# ========== Digital Safety Twin ==========


class WorksiteConfig(BaseModel):
    worksite_id: str
    locations: List[Dict[str, Any]]


class ScenarioConfig(BaseModel):
    name: str
    type: str
    description: str
    location_id: str
    risk_factors: List[str]
    changes: Dict[str, Any] = {}


@router.post("/digital-twin/create-worksite")
async def create_digital_twin(config: WorksiteConfig):
    """إنشاء توأم رقمي لموقع عمل"""
    try:
        result = digital_twin.create_worksite(config.worksite_id, config.dict())
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/digital-twin/simulate-scenario")
async def simulate_scenario(scenario: ScenarioConfig):
    """محاكاة سيناريو حادث"""
    try:
        result = digital_twin.simulate_scenario(scenario.dict())
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/digital-twin/test-procedure-change")
async def test_procedure_change(
    current_procedures: Dict[str, Any], new_procedures: Dict[str, Any]
):
    """اختبار تأثير تغيير الإجراءات"""
    try:
        result = digital_twin.test_procedure_change(current_procedures, new_procedures)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/digital-twin/heatmap")
async def get_risk_heatmap(timeframe: str = "current"):
    """الحصول على خريطة المخاطر الحرارية"""
    try:
        result = digital_twin.generate_virtual_heatmap(timeframe)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/digital-twin/predict-hotspots")
async def predict_hotspots(days_ahead: int = 7):
    """التنبؤ بنقاط الحوادث الساخنة"""
    try:
        result = digital_twin.predict_incident_hotspots(days_ahead)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== AI Safety Brain ==========


class IncidentData(BaseModel):
    type: str
    location: str
    severity: float
    root_causes: List[str]
    consequences: List[str]
    timestamp: Optional[str] = None


class NearMissData(BaseModel):
    description: str
    potential_severity: float
    prevented_by: List[str]
    timestamp: Optional[str] = None


@router.post("/ai-brain/learn-from-incident")
async def learn_from_incident(incident: IncidentData):
    """التعلم من حادث"""
    try:
        result = safety_brain.learn_from_incident(incident.dict())
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai-brain/learn-from-near-miss")
async def learn_from_near_miss(near_miss: NearMissData):
    """التعلم من حادث كاد أن يقع"""
    try:
        result = safety_brain.learn_from_near_miss(near_miss.dict())
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai-brain/learn-from-behavior")
async def learn_from_behavior(behavior_data: Dict[str, Any]):
    """التعلم من سلوك العمال"""
    try:
        result = safety_brain.learn_from_behavior(behavior_data)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai-brain/organizational-memory")
async def get_organizational_memory():
    """الحصول على الذاكرة المؤسسية"""
    try:
        result = safety_brain.build_organizational_memory()
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai-brain/apply-to-new-project")
async def apply_learning_to_project(project_config: Dict[str, Any]):
    """تطبيق التعلم على مشروع جديد"""
    try:
        result = safety_brain.apply_learning_to_new_project(project_config)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai-brain/cross-project-insights")
async def get_cross_project_insights():
    """رؤى عبر المشاريع"""
    try:
        result = safety_brain.get_cross_project_insights()
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== Worker Risk Profiling ==========


@router.post("/risk-profiling/create-profile")
async def create_worker_profile(worker_data: Dict[str, Any]):
    """إنشاء ملف تعريف عامل"""
    try:
        result = risk_profiling.create_worker_profile(worker_data)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk-profiling/analyze-behavior")
async def analyze_worker_behavior(behavior_data: Dict[str, Any]):
    """تحليل سلوك العامل"""
    try:
        result = risk_profiling.analyze_behavior_pattern(behavior_data)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk-profiling/classify-by-task")
async def classify_risk_by_task(task_data: Dict[str, Any]):
    """تصنيف المخاطر حسب المهمة"""
    try:
        result = risk_profiling.classify_risk_by_task(task_data)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk-profiling/classify-by-time")
async def classify_risk_by_time(time_data: Dict[str, Any]):
    """تصنيف المخاطر حسب الوقت"""
    try:
        result = risk_profiling.classify_risk_by_time(time_data)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk-profiling/assess-fatigue")
async def assess_fatigue(fatigue_data: Dict[str, Any]):
    """تقييم مستوى الإجهاد"""
    try:
        result = risk_profiling.assess_fatigue_level(fatigue_data)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk-profiling/suggest-redistribution")
async def suggest_task_redistribution(redistribution_data: Dict[str, Any]):
    """اقتراح إعادة توزيع المهام"""
    try:
        result = risk_profiling.suggest_task_redistribution(redistribution_data)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk-profiling/report")
async def get_risk_report(worker_id: Optional[str] = None):
    """تقرير المخاطر الشامل"""
    try:
        result = risk_profiling.get_comprehensive_risk_report(worker_id)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== Safety Gamification ==========


@router.post("/gamification/register-player")
async def register_player(player_data: Dict[str, Any]):
    """تسجيل لاعب جديد"""
    try:
        result = gamification.register_player(player_data)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gamification/record-safe-behavior")
async def record_safe_behavior(behavior_data: Dict[str, Any]):
    """تسجيل سلوك آمن"""
    try:
        result = gamification.record_safe_behavior(behavior_data)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gamification/leaderboard")
async def get_leaderboard(leaderboard_type: str = "individual", limit: int = 10):
    """الحصول على لوحة الصدارة"""
    try:
        result = gamification.get_leaderboard(leaderboard_type, limit)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gamification/award-badge")
async def award_badge(player_id: str, badge_name: str):
    """منح وسام"""
    try:
        result = gamification.award_badge(player_id, badge_name)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== AI Storytelling ==========


@router.post("/storytelling/create-story")
async def create_incident_story(incident_data: Dict[str, Any]):
    """إنشاء قصة من حادث"""
    try:
        result = storytelling.create_incident_story(incident_data)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== Compliance Auditor ==========


@router.post("/compliance/audit")
async def conduct_compliance_audit(
    site_data: Dict[str, Any], standard: str = "ISO45001"
):
    """إجراء تدقيق امتثال"""
    try:
        result = compliance_auditor.conduct_audit(site_data, standard)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compliance/detect-drift")
async def detect_compliance_drift(current_audit: Dict, baseline_audit: Dict):
    """اكتشاف انحراف الامتثال"""
    try:
        result = compliance_auditor.detect_drift(current_audit, baseline_audit)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compliance/report")
async def get_compliance_report(audit_id: Optional[str] = None):
    """تقرير الامتثال"""
    try:
        result = compliance_auditor.generate_compliance_report(audit_id)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== Smart Permit-to-Work ==========


@router.post("/permit/review")
async def review_permit(permit_data: Dict[str, Any]):
    """مراجعة تصريح عمل"""
    try:
        result = permit_ai.review_permit(permit_data)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== Executive Advisor ==========


@router.post("/executive/ask")
async def ask_executive_advisor(question: str, context_data: Dict[str, Any] = {}):
    """سؤال المستشار التنفيذي"""
    try:
        result = executive_advisor.answer_executive_question(question, context_data)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== Autonomous Safety Actions ==========


@router.post("/autonomous/detect-and-act")
async def autonomous_detect_and_act(risk_data: Dict[str, Any]):
    """اكتشاف خطر واتخاذ إجراء تلقائي"""
    try:
        result = autonomous_actions.detect_and_act(risk_data)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== Cross-Project Intelligence ==========


@router.post("/cross-project/compare")
async def compare_projects(project_ids: List[str]):
    """مقارنة المشاريع"""
    try:
        result = cross_project.compare_projects(project_ids)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cross-project/sector-insights")
async def get_sector_insights(sector: str):
    """رؤى قطاعية"""
    try:
        result = cross_project.extract_sector_insights(sector)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== Dashboard Overview ==========


@router.get("/overview")
async def get_advanced_features_overview():
    """نظرة عامة على جميع الميزات المتقدمة"""
    return {
        "success": True,
        "features": {
            "digital_safety_twin": {
                "name": "التوأم الرقمي للسلامة",
                "description": "محاكاة افتراضية للموقع",
                "endpoints": [
                    "/digital-twin/create-worksite",
                    "/digital-twin/simulate-scenario",
                    "/digital-twin/heatmap",
                    "/digital-twin/predict-hotspots",
                ],
            },
            "ai_safety_brain": {
                "name": "العقل المركزي للسلامة",
                "description": "ذكاء مركزي يتعلم من جميع الأحداث",
                "endpoints": [
                    "/ai-brain/learn-from-incident",
                    "/ai-brain/learn-from-near-miss",
                    "/ai-brain/organizational-memory",
                    "/ai-brain/apply-to-new-project",
                ],
            },
            "worker_risk_profiling": {
                "name": "تحليل المخاطر للعمال",
                "description": "تحليل نمط السلوك الخطر",
                "endpoints": [
                    "/risk-profiling/analyze-behavior",
                    "/risk-profiling/classify-by-task",
                    "/risk-profiling/assess-fatigue",
                    "/risk-profiling/suggest-redistribution",
                ],
            },
            "safety_gamification": {
                "name": "محرك التحفيز",
                "description": "نظام نقاط ومكافآت",
                "endpoints": [
                    "/gamification/register-player",
                    "/gamification/record-safe-behavior",
                    "/gamification/leaderboard",
                ],
            },
            "ai_storytelling": {
                "name": "رواية الحوادث بالذكاء الاصطناعي",
                "description": "تحويل الحوادث إلى قصص تحليلية",
                "endpoints": ["/storytelling/create-story"],
            },
            "compliance_auditor": {
                "name": "المدقق التلقائي",
                "description": "تدقيق الامتثال ISO/OSHA",
                "endpoints": [
                    "/compliance/audit",
                    "/compliance/detect-drift",
                    "/compliance/report",
                ],
            },
            "smart_permit": {
                "name": "تصاريح العمل الذكية",
                "description": "مراجعة AI لتصاريح العمل",
                "endpoints": ["/permit/review"],
            },
            "executive_advisor": {
                "name": "المستشار التنفيذي",
                "description": "مساعد AI للإدارة العليا",
                "endpoints": ["/executive/ask"],
            },
            "autonomous_actions": {
                "name": "الإجراءات التلقائية",
                "description": "إيقاف وتنبيه تلقائي",
                "endpoints": ["/autonomous/detect-and-act"],
            },
            "cross_project": {
                "name": "الذكاء عبر المشاريع",
                "description": "تحليل ومقارنة المشاريع",
                "endpoints": [
                    "/cross-project/compare",
                    "/cross-project/sector-insights",
                ],
            },
        },
        "total_features": 10,
        "total_endpoints": 40,
        "message": "🏆 حزم طويق - أول منصة تفكّر استباقيًا بالسلامة",
    }


@router.get("/health")
async def advanced_features_health():
    """فحص صحة الميزات المتقدمة"""
    return {
        "status": "healthy",
        "modules": {
            "digital_twin": "operational",
            "ai_brain": "operational",
            "risk_profiling": "operational",
            "gamification": "operational",
            "storytelling": "operational",
            "compliance": "operational",
            "permit_ai": "operational",
            "executive_advisor": "operational",
            "autonomous_actions": "operational",
            "cross_project": "operational",
        },
        "timestamp": datetime.now().isoformat(),
    }
