"""
Next-Level Innovations API - واجهة برمجية للميزات المتقدمة
API شامل لجميع الابتكارات الثورية في النظام
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime

# استيراد الوحدات المتقدمة
from .organization_graph import (
    organization_graph, Node, Role, Permission, 
    AuthorityLevel, RiskLevel
)
from .owner_control import owner_control
from .explainable_ai import (
    ExplainableDecision, DecisionType, ConfidenceLevel,
    liability_shield
)
from .advanced_detection import micro_behavior_detector, stress_detector
from .shadow_simulation import shadow_simulator, budget_optimizer

router = APIRouter()


# ===== نماذج البيانات =====

class CreateRoleRequest(BaseModel):
    owner_id: str
    role_data: Dict


class ModifyRoleRequest(BaseModel):
    owner_id: str
    role_id: str
    modifications: Dict


class DeleteRoleRequest(BaseModel):
    owner_id: str
    role_id: str


class ConstitutionalRuleRequest(BaseModel):
    owner_id: str
    rule: Dict


class CreatePersonRequest(BaseModel):
    owner_id: str
    person_data: Dict


class AssignRoleRequest(BaseModel):
    owner_id: str
    person_id: str
    role_id: str


class BehaviorAnalysisRequest(BaseModel):
    worker_id: str
    video_data: Dict
    context: Dict = {}


class StressAnalysisRequest(BaseModel):
    worker_id: str
    signals: Dict


class ShadowSimulationRequest(BaseModel):
    actual_event: Dict
    alternative_scenarios: List[str]


class BudgetOptimizationRequest(BaseModel):
    total_budget: float
    risk_areas: List[Dict]


# ===== Owner Control Center Endpoints =====

@router.post("/owner/role/create")
async def create_role(request: CreateRoleRequest):
    """
    إنشاء دور جديد (Owner فقط)
    
    المثال:
    ```json
    {
        "owner_id": "owner_001",
        "role_data": {
            "id": "senior_supervisor",
            "name": "Senior Supervisor",
            "authority": "SUPERVISOR",
            "permissions": ["VIEW_DASHBOARD", "STOP_WORK"],
            "dynamic_rules": [
                {
                    "condition": "risk_level == 'CRITICAL'",
                    "grant": ["OVERRIDE_AI"]
                }
            ]
        }
    }
    ```
    """
    success, message = owner_control.create_role(request.owner_id, request.role_data)
    
    if not success:
        raise HTTPException(status_code=403, detail=message)
    
    return {"success": True, "message": message}


@router.post("/owner/role/modify")
async def modify_role(request: ModifyRoleRequest):
    """تعديل دور موجود (Owner فقط)"""
    success, message = owner_control.modify_role(
        request.owner_id, 
        request.role_id, 
        request.modifications
    )
    
    if not success:
        raise HTTPException(status_code=403, detail=message)
    
    return {"success": True, "message": message}


@router.post("/owner/role/delete")
async def delete_role(request: DeleteRoleRequest):
    """حذف دور (Owner فقط)"""
    success, message = owner_control.delete_role(request.owner_id, request.role_id)
    
    if not success:
        raise HTTPException(status_code=403, detail=message)
    
    return {"success": True, "message": message}


@router.post("/owner/constitution/add-rule")
async def add_constitutional_rule(request: ConstitutionalRuleRequest):
    """
    إضافة قاعدة دستورية (Owner فقط)
    
    المثال:
    ```json
    {
        "owner_id": "owner_001",
        "rule": {
            "type": "mandatory",
            "requirement": "ppe_required",
            "description": "لا عمل بدون معدات الحماية",
            "violation_message": "العمل بدون PPE محظور دستورياً",
            "active": true
        }
    }
    ```
    """
    success, message = owner_control.set_constitutional_rule(request.owner_id, request.rule)
    
    if not success:
        raise HTTPException(status_code=403, detail=message)
    
    return {"success": True, "message": message}


@router.get("/owner/constitution")
async def get_constitution(owner_id: str):
    """الحصول على الدستور الكامل"""
    # التحقق من صلاحية المالك
    if not owner_control._verify_owner(owner_id):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    return organization_graph.constitution.to_dict()


@router.post("/owner/person/create")
async def create_person(request: CreatePersonRequest):
    """
    إنشاء شخص في النظام
    
    المثال:
    ```json
    {
        "owner_id": "owner_001",
        "person_data": {
            "id": "person_123",
            "name": "أحمد محمد",
            "role_id": "supervisor",
            "contact": {
                "email": "ahmad@example.com",
                "phone": "+966501234567"
            },
            "department": "الإنشاءات",
            "manages_locations": ["site_a", "site_b"]
        }
    }
    ```
    """
    success, message = owner_control.create_person(request.owner_id, request.person_data)
    
    if not success:
        raise HTTPException(status_code=403, detail=message)
    
    return {"success": True, "message": message}


@router.post("/owner/person/assign-role")
async def assign_role_to_person(request: AssignRoleRequest):
    """تعيين دور لشخص"""
    success, message = owner_control.assign_role(
        request.owner_id,
        request.person_id,
        request.role_id
    )
    
    if not success:
        raise HTTPException(status_code=403, detail=message)
    
    return {"success": True, "message": message}


@router.get("/owner/overview")
async def get_system_overview(owner_id: str):
    """نظرة عامة على النظام (Owner فقط)"""
    overview = owner_control.get_system_overview(owner_id)
    
    if not overview:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    return overview


@router.get("/owner/audit-log")
async def get_audit_log(owner_id: str, action_type: Optional[str] = None):
    """الحصول على سجل المراجعة"""
    filters = {}
    if action_type:
        filters["action_type"] = action_type
    
    logs = owner_control.get_audit_log(owner_id, filters)
    
    if not logs and not owner_control._verify_owner(owner_id):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    return {"logs": logs, "total": len(logs)}


# ===== Organization Graph Endpoints =====

@router.get("/organization/graph/export")
async def export_organization_graph():
    """تصدير الرسم البياني التنظيمي الكامل"""
    return organization_graph.export_graph()


@router.get("/organization/find-responsible")
async def find_responsible_persons(location: str, risk_level: str):
    """
    إيجاد المسؤولين عن موقع
    
    المعاملات:
    - location: معرف الموقع
    - risk_level: مستوى الخطر (LOW, MEDIUM, HIGH, CRITICAL)
    """
    try:
        risk = RiskLevel[risk_level.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid risk level: {risk_level}")
    
    responsible = organization_graph.find_responsible_persons(location, risk)
    
    return {
        "location": location,
        "risk_level": risk_level,
        "responsible_persons": responsible
    }


@router.get("/organization/alert-chain")
async def get_alert_chain(location: str, risk_level: str):
    """الحصول على سلسلة التنبيهات لموقع وخطر"""
    try:
        risk = RiskLevel[risk_level.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid risk level: {risk_level}")
    
    chain = organization_graph.get_alert_chain(location, risk)
    
    # الحصول على تفاصيل الأشخاص
    persons = []
    for person_id in chain:
        if person_id in organization_graph.nodes:
            person = organization_graph.nodes[person_id]
            persons.append({
                "id": person.id,
                "name": person.name,
                "role": person.metadata.get("role_id"),
                "contact": person.metadata.get("contact", {})
            })
    
    return {
        "location": location,
        "risk_level": risk_level,
        "alert_chain": persons
    }


@router.post("/organization/check-permission")
async def check_permission(person_id: str, permission: str, context: Dict = Body(...)):
    """
    التحقق من صلاحية شخص
    
    المثال:
    ```json
    {
        "person_id": "person_123",
        "permission": "STOP_WORK",
        "context": {
            "risk_level": "HIGH",
            "location": "site_a",
            "time_of_day": 14
        }
    }
    ```
    """
    try:
        perm = Permission[permission.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid permission: {permission}")
    
    has_permission = organization_graph.check_permission(person_id, perm, context)
    
    return {
        "person_id": person_id,
        "permission": permission,
        "has_permission": has_permission,
        "context": context
    }


@router.post("/organization/validate-action")
async def validate_action(action: str, person_id: str, context: Dict = Body(...)):
    """
    التحقق من صحة إجراء
    يتحقق من الدستور والصلاحيات
    """
    valid, message = organization_graph.validate_action(action, person_id, context)
    
    return {
        "action": action,
        "person_id": person_id,
        "valid": valid,
        "message": message,
        "context": context
    }


# ===== Explainable AI Endpoints =====

@router.post("/ai/decision/create")
async def create_explainable_decision(
    decision_type: str,
    result: Dict,
    reasoning: List[str],
    evidence: List[Dict],
    confidence: float
):
    """
    إنشاء قرار AI قابل للتفسير
    
    المثال:
    ```json
    {
        "decision_type": "WORK_STOP",
        "result": {"action": "stop", "reason": "critical_risk"},
        "reasoning": [
            "اكتشاف خطر حرج في الموقع",
            "عدم ارتداء معدات الحماية",
            "تاريخ حوادث في نفس الموقع"
        ],
        "evidence": [
            {"type": "image", "data": "base64...", "weight": 0.9},
            {"type": "sensor", "data": {"temp": 45}, "weight": 0.7}
        ],
        "confidence": 0.92
    }
    ```
    """
    try:
        dec_type = DecisionType[decision_type.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid decision type: {decision_type}")
    
    decision = ExplainableDecision(dec_type, result)
    
    # إضافة الأسباب
    for reason in reasoning:
        decision.add_reasoning(reason)
    
    # إضافة الأدلة
    for ev in evidence:
        decision.add_evidence(
            ev.get("type", "unknown"),
            ev.get("data"),
            ev.get("weight", 1.0)
        )
    
    # تعيين مستوى الثقة
    decision.set_confidence(confidence)
    
    return {
        "decision_id": decision.id,
        "explanation": decision.generate_explanation("ar"),
        "summary": decision.generate_summary("ar")
    }


@router.post("/liability/log-incident")
async def log_incident_for_liability(incident_id: str, details: Dict = Body(...)):
    """تسجيل حادث في سجل المسؤولية"""
    liability_shield.log_incident(incident_id, details)
    
    return {"success": True, "incident_id": incident_id}


@router.post("/liability/log-observation")
async def log_observation(incident_id: str, observer: Dict, observation: str):
    """تسجيل من رأى الخطر"""
    liability_shield.log_observation(incident_id, observer, observation)
    
    return {"success": True}


@router.get("/liability/report/{incident_id}")
async def get_liability_report(incident_id: str, language: str = "ar"):
    """توليد تقرير مسؤولية قانوني"""
    report = liability_shield.generate_liability_report(incident_id, language)
    
    return report


# ===== Advanced Detection Endpoints =====

@router.post("/detection/behavior/analyze")
async def analyze_worker_behavior(request: BehaviorAnalysisRequest):
    """
    تحليل سلوك عامل من الفيديو
    
    المثال:
    ```json
    {
        "worker_id": "worker_456",
        "video_data": {
            "movement_speed": 0.4,
            "stability_score": 0.55,
            "action_starts": 3,
            "pause_duration": 7,
            "coordination_score": 0.65
        },
        "context": {
            "task": "welding",
            "location": "site_a",
            "time": "14:30"
        }
    }
    ```
    """
    result = micro_behavior_detector.analyze_behavior(
        request.worker_id,
        request.video_data,
        request.context
    )
    
    return result


@router.get("/detection/behavior/profile/{worker_id}")
async def get_worker_risk_profile(worker_id: str):
    """الحصول على ملف تعريف مخاطر العامل"""
    profile = micro_behavior_detector.get_worker_profile(worker_id)
    
    return profile


@router.post("/detection/stress/analyze")
async def analyze_stress_signals(request: StressAnalysisRequest):
    """
    تحليل مؤشرات التوتر والضغط
    
    المثال:
    ```json
    {
        "worker_id": "worker_456",
        "signals": {
            "movement_pattern": "agitated",
            "task_speed": 1.8,
            "error_rate": 0.35,
            "continuous_work_hours": 9
        }
    }
    ```
    """
    result = stress_detector.analyze_stress_signals(
        request.worker_id,
        request.signals
    )
    
    return result


# ===== Shadow Simulation Endpoints =====

@router.post("/simulation/shadow/run")
async def run_shadow_simulation(request: ShadowSimulationRequest):
    """
    تشغيل محاكاة ظل لسيناريوهات "ماذا لو"
    
    المثال:
    ```json
    {
        "actual_event": {
            "event_id": "evt_123",
            "type": "near_miss",
            "risk_level": 0.6,
            "severity": 2,
            "outcome": "safe",
            "action_taken": "work_stopped",
            "location": "site_a"
        },
        "alternative_scenarios": [
            "what_if_no_action",
            "what_if_ignored_warning",
            "what_if_no_ppe"
        ]
    }
    ```
    """
    result = shadow_simulator.run_shadow_simulation(
        request.actual_event,
        request.alternative_scenarios
    )
    
    return result


@router.get("/simulation/shadow/report/{simulation_id}")
async def get_shadow_simulation_report(simulation_id: str, language: str = "ar"):
    """الحصول على تقرير محاكاة ظل"""
    report = shadow_simulator.generate_what_if_report(simulation_id, language)
    
    return report


@router.get("/simulation/shadow/value-saved")
async def get_saved_value_summary(days: int = 30):
    """ملخص القيمة المحفوظة من المحاكاة"""
    summary = shadow_simulator.get_saved_value_summary(days)
    
    return summary


# ===== Budget Optimization Endpoints =====

@router.post("/budget/optimize")
async def optimize_safety_budget(request: BudgetOptimizationRequest):
    """
    تحسين توزيع ميزانية السلامة
    
    المثال:
    ```json
    {
        "total_budget": 500000,
        "risk_areas": [
            {
                "name": "منطقة اللحام",
                "risk_level": 0.75,
                "past_incidents": 5,
                "worker_count": 25
            },
            {
                "name": "منطقة الحفر",
                "risk_level": 0.65,
                "past_incidents": 3,
                "worker_count": 15
            }
        ]
    }
    ```
    """
    result = budget_optimizer.optimize_budget(
        request.total_budget,
        request.risk_areas
    )
    
    return result


# ===== Health Check =====

@router.get("/innovations/health")
async def innovations_health():
    """فحص صحة واجهة الابتكارات"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "organization_graph": True,
            "owner_control": True,
            "explainable_ai": True,
            "advanced_detection": True,
            "shadow_simulation": True,
            "budget_optimizer": True
        },
        "statistics": {
            "total_roles": len(organization_graph.roles),
            "total_nodes": len(organization_graph.nodes),
            "constitutional_rules": len(organization_graph.constitution.rules),
            "audit_log_entries": len(owner_control.audit_log),
            "liability_log_entries": len(liability_shield.liability_log),
            "simulations_run": len(shadow_simulator.simulations)
        }
    }
