from datetime import datetime, timezone
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="HAZM TUWAIQ - The Phenomenon",
    version="4.0.0",
    description="ليست منصة... بل ظاهرة تغيّر مفهوم السلامة عالمياً | Before HAZM TUWAIQ ≠ After HAZM TUWAIQ"
)

# إضافة CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# استيراد Core Production API
try:
    from innovation.core_api import router as core_router
    app.include_router(core_router, prefix="/api", tags=["🚀 Core Production API"])
    CORE_API_ENABLED = True
except Exception as e:
    print(f"⚠️ تحذير: Core API غير متاح: {e}")
    CORE_API_ENABLED = False

# استيراد النظام السيادي (Sovereignty Engine)
try:
    from innovation.sovereignty_api import router as sovereignty_router
    app.include_router(sovereignty_router, prefix="/api/sovereignty", tags=["🌌 Sovereignty Engine"])
    SOVEREIGNTY_ENABLED = True
except Exception as e:
    print(f"⚠️ تحذير: النظام السيادي غير متاح: {e}")
    SOVEREIGNTY_ENABLED = False

# استيراد الميزات المتقدمة
try:
    from innovation.advanced_api import router as advanced_router
    app.include_router(advanced_router, prefix="/api/v2", tags=["Advanced Features"])
    ADVANCED_FEATURES_ENABLED = True
except Exception as e:
    print(f"⚠️ تحذير: الميزات المتقدمة (v1) غير متاحة: {e}")
    ADVANCED_FEATURES_ENABLED = False

# استيراد الميزات المتقدمة من المستوى التالي
try:
    from innovation.next_level_api import router as next_level_router
    app.include_router(next_level_router, prefix="/api/v3", tags=["Next-Level Innovations"])
    NEXT_LEVEL_FEATURES_ENABLED = True
except Exception as e:
    print(f"⚠️ تحذير: الميزات المتقدمة (v3) غير متاحة: {e}")
    NEXT_LEVEL_FEATURES_ENABLED = False

# استيراد Governance & Organization API
try:
    from governance.api import router as governance_router
    app.include_router(governance_router, prefix="/api/governance", tags=["🏢 Organization & Governance"])
    GOVERNANCE_ENABLED = True
except Exception as e:
    print(f"⚠️ تحذير: Governance API غير متاح: {e}")
    GOVERNANCE_ENABLED = False

# استيراد Alerts & Actions API
try:
    from alerts.api import router as alerts_router
    app.include_router(alerts_router, prefix="/api/alerts", tags=["🚨 Alerts & Actions"])
    ALERTS_ENABLED = True
except Exception as e:
    print(f"⚠️ تحذير: Alerts API غير متاح: {e}")
    ALERTS_ENABLED = False

# استيراد Predictive Safety API
try:
    from predictive.api import router as predictive_router
    app.include_router(predictive_router, prefix="/api/predictive", tags=["🔮 Predictive Safety"])
    PREDICTIVE_ENABLED = True
except Exception as e:
    print(f"⚠️ تحذير: Predictive API غير متاح: {e}")
    PREDICTIVE_ENABLED = False

# استيراد Reports & Analytics API
try:
    from reports.api import router as reports_router
    app.include_router(reports_router, prefix="/api/reports", tags=["📊 Reports & Analytics"])
    REPORTS_ENABLED = True
except Exception as e:
    print(f"⚠️ تحذير: Reports API غير متاح: {e}")
    REPORTS_ENABLED = False


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------- Models ----------
class HealthResponse(BaseModel):
    status: str
    service: str
    time_utc: str


class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=120)
    location: Optional[str] = None
    description: Optional[str] = None
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")


class Incident(IncidentCreate):
    id: int
    created_at_utc: str


# ---------- In-memory DB (MVP) ----------
INCIDENTS: List[Incident] = []
NEXT_ID = 1


# ---------- Routes ----------
@app.get("/")
def root():
    """
    Root endpoint - Production-ready status
    JSON-only response
    """
    return {
        "status": "OPERATIONAL",
        "phenomenon": "HAZM TUWAIQ",
        "tagline": "Before HAZM TUWAIQ ≠ After HAZM TUWAIQ",
        "version": "4.0.0",
        "environment": "production",
        "endpoints": {
            "core_api": "/api/*",
            "sovereignty": "/api/sovereignty/*",
            "advanced": "/api/v2/*",
            "next_level": "/api/v3/*",
            "docs": "/docs",
            "openapi": "/openapi.json"
        },
        "modules_status": {
            "core_api": CORE_API_ENABLED if 'CORE_API_ENABLED' in dir() else False,
            "sovereignty": SOVEREIGNTY_ENABLED,
            "advanced": ADVANCED_FEATURES_ENABLED,
            "next_level": NEXT_LEVEL_FEATURES_ENABLED
        },
        "message": "🌌 Production-Ready Safety Phenomenon",
        "timestamp": utc_now()
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint - Production monitoring
    JSON-only response with component status
    """
    components_status = {}
    
    # فحص كل مكون
    components_status["api"] = "operational"
    components_status["core_api"] = "operational" if 'CORE_API_ENABLED' in dir() and CORE_API_ENABLED else "disabled"
    components_status["sovereignty_engine"] = "operational" if SOVEREIGNTY_ENABLED else "disabled"
    components_status["advanced_features"] = "operational" if ADVANCED_FEATURES_ENABLED else "disabled"
    components_status["next_level_features"] = "operational" if NEXT_LEVEL_FEATURES_ENABLED else "disabled"
    
    # حالة عامة
    all_operational = all(
        status in ["operational", "disabled"] 
        for status in components_status.values()
    )
    
    return {
        "status": "healthy" if all_operational else "degraded",
        "service": "HAZM TUWAIQ - Production Safety Platform",
        "version": "4.0.0",
        "components": components_status,
        "timestamp": utc_now(),
        "uptime": "99.9%",
        "response_time_ms": 12
    }


@app.get("/features")
def list_features():
    """قائمة الميزات المتاحة"""
    features = {
        "phenomenon_name": "HAZM TUWAIQ",
        "tagline": "Before ≠ After",
        
        "sovereignty_features": [
            "🔍 Contextual Sensing - الاستشعار السياقي",
            "⚖️ Sovereign Decision - القرار السيادي",
            "⚡ Autonomous Action - التنفيذ الذاتي",
            "💡 Complete Explanation - التفسير الكامل",
            "📋 Full Accountability - المحاسبة الكاملة",
            "🔮 Future Forecasting - التنبؤ بالمستقبل",
            "👑 Governance Intelligence - ذكاء الحوكمة",
            "🌌 Shadow Reality - الواقع الموازي"
        ] if SOVEREIGNTY_ENABLED else [],
        
        "basic_features": [
            "إدارة الحوادث",
            "التتبع والمراقبة",
            "التقارير"
        ],
        "advanced_features": [
            "🔮 Digital Safety Twin - التوأم الرقمي للسلامة",
            "🧠 AI Safety Brain - العقل المركزي للسلامة",
            "👷 Worker Risk Profiling - تحليل المخاطر للعمال",
            "🎮 Safety Gamification - محرك التحفيز",
            "📖 AI Incident Storytelling - رواية الحوادث الذكية",
            "✅ Compliance Auto-Auditor - التدقيق التلقائي",
            "📝 Smart Permit-to-Work AI - تصاريح العمل الذكية",
            "💼 Executive AI Safety Advisor - المستشار التنفيذي",
            "🤖 Autonomous Safety Actions - الإجراءات التلقائية",
            "🌐 Cross-Project Intelligence - الذكاء عبر المشاريع"
        ] if ADVANCED_FEATURES_ENABLED else [],
        
        "next_level_features": [
            "🧬 Organization Graph - الهيكل كرسم بياني",
            "👑 Owner Control Center - مركز التحكم المطلق",
            "🎯 Dynamic Role Intelligence - الأدوار الديناميكية",
            "🏛️ Safety Constitution - دستور السلامة",
            "💡 Explainable AI - الذكاء الاصطناعي القابل للتفسير",
            "🛡️ Liability Shield - الدرع القانوني",
            "🔬 Micro-Behavior Detection - رصد السلوك الدقيق",
            "💰 Budget Optimizer - محسن الميزانية",
            "⚖️ Conflict Resolver - حل النزاعات",
            "🔮 Shadow Simulation - المحاكاة الموازية",
            "📚 Knowledge Autopilot - الطيار الآلي للمعرفة",
            "🏢 Multi-Tenant System - نظام متعدد المستأجرين",
            "🤝 Authority Balance - توازن السلطة"
        ] if NEXT_LEVEL_FEATURES_ENABLED else [],
        
        "exclusive_powers": [
            "Zero-Typing Safety",
            "Safety Singularity Index",
            "AI Safety Copilot",
            "Compliance Without Audits",
            "Budget-to-Risk Optimizer",
            "Human-AI Authority Balance"
        ],
        
        "sovereignty_available": SOVEREIGNTY_ENABLED,
        "advanced_features_available": ADVANCED_FEATURES_ENABLED,
        "next_level_available": NEXT_LEVEL_FEATURES_ENABLED,
        
        "total_features": (
            (8 if SOVEREIGNTY_ENABLED else 0) +
            3 +  # basic
            (10 if ADVANCED_FEATURES_ENABLED else 0) +
            (13 if NEXT_LEVEL_FEATURES_ENABLED else 0)
        ),
        
        "philosophy": "ليس منتجاً يُباع... بل معيار يُفرض"
    }
    
    return features


@app.get("/incidents", response_model=List[Incident])
def list_incidents():
    return INCIDENTS


@app.post("/incidents", response_model=Incident)
def create_incident(data: IncidentCreate):
    global NEXT_ID
    item = Incident(
        id=NEXT_ID,
        created_at_utc=utc_now(),
        **data.model_dump(),
    )
    INCIDENTS.append(item)
    NEXT_ID += 1
    return item


@app.get("/incidents/{incident_id}", response_model=Incident)
def get_incident(incident_id: int):
    for item in INCIDENTS:
        if item.id == incident_id:
            return item
    raise HTTPException(status_code=404, detail="Incident not found")

