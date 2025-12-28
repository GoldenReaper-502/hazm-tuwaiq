from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Header, Query, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from starlette.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
from threading import Lock
import ai_engine
import report_generator
import export_utils
import cctv
import uuid
from pydantic import BaseModel, Field
import os
import json
import logging
import base64
from io import BytesIO

APP_NAME = "Hazm Tuwaiq API"
APP_VERSION = "0.1.0"

# =========================
# Logging Configuration
# =========================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =========================
# Simple Security (Optional)
# =========================
# ضع API Key داخل Render Environment:
# HAZM_API_KEY = "anything"
# إذا ما ضبطته = ما فيه حماية (يسمح للجميع)
HAZM_API_KEY = os.getenv("HAZM_API_KEY", "").strip()


def require_api_key(x_api_key: Optional[str]) -> None:
    if not HAZM_API_KEY:
        return  # No protection enabled
    if not x_api_key or x_api_key.strip() != HAZM_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# =========================
# App
# =========================
app = FastAPI(title=APP_NAME, version=APP_VERSION)

load_dotenv()

# CORS configuration from env or default to local dev origins
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000").split(",")
cors_origins = [o.strip() for o in cors_origins if o.strip()]
if not cors_origins:
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Initialize heavy resources at startup (YOLO model)."""
    try:
        model = ai_engine.init_model()
        if model is not None:
            logger.info("AI engine: YOLO model loaded at startup")
        else:
            logger.warning("AI engine: YOLO model not available (using mock)")
    except Exception as e:
        logger.exception(f"AI engine init failed: {e}")

    # Initialize CCTV manager and start enabled cameras (best-effort)
    try:
        mgr = cctv.get_manager()
        cams = mgr.list_cameras()
        for cam in cams:
            try:
                if cam.get("enabled"):
                    mgr.start_camera(cam.get("id"))
                    logger.info(f"Started camera at startup: {cam.get('id')}")
            except Exception as ce:
                logger.warning(f"Failed to start camera {cam.get('id')}: {ce}")
    except Exception as e:
        logger.exception(f"CCTV manager init failed: {e}")

# Reports storage (file-based simple storage)
STORAGE_DIR = Path(__file__).resolve().parent
REPORTS_FILE = STORAGE_DIR / "reports.json"
REPORTS_LOCK = Lock()

if not REPORTS_FILE.exists():
    REPORTS_FILE.write_text("[]")


# =========================
# Helpers
# =========================
def utc_now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def new_id(prefix: str, counter: int) -> str:
    return f"{prefix}_{counter:06d}"


# =========================
# Detection & Chat Models (New)
# =========================
class DetectionRequest(BaseModel):
    """نموذج طلب الكشف - يحتوي على صورة بصيغة base64"""
    frame_data: str = Field(..., description="صورة base64 من الكاميرا")
    timestamp: Optional[str] = None


class DetectionResult(BaseModel):
    """نموذج نتيجة الكشف"""
    id: str
    timestamp: str
    objects: List[Dict[str, Any]] = Field(default_factory=list)
    raw_response: Optional[Dict[str, Any]] = None
    is_valid: bool = True


class ChatMessage(BaseModel):
    """رسالة دردشة واحدة"""
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=5000)
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    """طلب دردشة - قد يتضمن نتيجة كشف"""
    message: str = Field(..., min_length=1, max_length=5000)
    detection_result: Optional[DetectionResult] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """رد الدردشة"""
    id: str
    session_id: str
    user_message: str
    assistant_response: str
    timestamp: str
    detection_attached: bool = False


# =========================
# In-memory "DB"
# =========================
DB: Dict[str, Any] = {
    "users": [],            # list[User]
    "incidents": [],        # list[Incident]
    "risk_assessments": [], # list[RiskAssessment]
    "inspections": [],      # list[Inspection]
    "uploads": [],          # list[UploadMeta]
    "detections": [],       # list[DetectionResult]
    "chat_sessions": {},    # dict[session_id] = list[ChatResponse]
}

COUNTERS = {
    "user": 1,
    "incident": 1,
    "ra": 1,
    "inspection": 1,
    "upload": 1,
    "detection": 1,
    "chat_msg": 1,
}

# Track last detection for chat integration
LAST_DETECTION: Optional[DetectionResult] = None

# Reports counters
REPORTS: List[Dict[str, Any]] = []  # Store reports in memory + file
REPORTS_LOCK = Lock()


# =========================
# Models
# =========================
class HealthResponse(BaseModel):
    status: str
    service: str
    time_utc: str
    version: str


class ApiMessage(BaseModel):
    ok: bool = True
    message: str


# ---- Auth / Users (MVP) ----
class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=80)
    email: str = Field(..., min_length=6, max_length=120)
    password: str = Field(..., min_length=4, max_length=120)
    role: str = Field(default="user", pattern="^(user|admin|hse|manager)$")


class UserLogin(BaseModel):
    email: str
    password: str


class User(BaseModel):
    id: str
    full_name: str
    email: str
    role: str
    created_at_utc: str


class AuthToken(BaseModel):
    token: str
    user: User


# ---- Incidents ----
class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=120)
    location: Optional[str] = Field(default=None, max_length=120)
    description: Optional[str] = Field(default=None, max_length=2000)
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    category: Optional[str] = Field(default=None, max_length=80)  # near-miss, injury, property damage...
    reported_by: Optional[str] = Field(default=None, max_length=80)  # name or id
    status: str = Field(default="open", pattern="^(open|investigating|closed)$")


class Incident(IncidentCreate):
    id: str
    created_at_utc: str
    updated_at_utc: str


# ---- Risk Assessment (RA) ----
class RiskAssessmentCreate(BaseModel):
    activity: str = Field(..., min_length=3, max_length=180)
    location: Optional[str] = Field(default=None, max_length=120)
    hazards: List[str] = Field(default_factory=list)
    controls: List[str] = Field(default_factory=list)
    risk_level: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    owner: Optional[str] = Field(default=None, max_length=80)
    status: str = Field(default="draft", pattern="^(draft|approved|archived)$")


class RiskAssessment(RiskAssessmentCreate):
    id: str
    created_at_utc: str
    updated_at_utc: str


# ---- Inspection / Checklist ----
class InspectionItem(BaseModel):
    question: str = Field(..., min_length=3, max_length=200)
    answer: str = Field(..., pattern="^(yes|no|na)$")
    note: Optional[str] = Field(default=None, max_length=500)


class InspectionCreate(BaseModel):
    site: str = Field(..., min_length=2, max_length=120)
    inspector: Optional[str] = Field(default=None, max_length=80)
    date_utc: Optional[str] = None
    items: List[InspectionItem] = Field(default_factory=list)
    overall_status: str = Field(default="open", pattern="^(open|closed)$")


class Inspection(InspectionCreate):
    id: str
    created_at_utc: str
    updated_at_utc: str


# ---- Upload metadata (MVP) ----
class UploadMeta(BaseModel):
    id: str
    filename: str
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None
    tag: Optional[str] = None
    created_at_utc: str


# ---- Reports (Smart) ----
class Report(BaseModel):
    """Auto-generated safety report from detection."""
    id: str
    detection_id: str
    timestamp: str
    location: Optional[str] = None
    risk_score: float
    risk_level: str  # HIGH, MEDIUM, LOW
    objects_count: int
    summary: str
    recommendations: List[str] = Field(default_factory=list)
    objects: List[Dict[str, Any]] = Field(default_factory=list)


# =========================
# Root + Health
# =========================
@app.get("/", response_model=HealthResponse)
def root():
    return HealthResponse(
        status="ok",
        service="Hazm Tuwaiq backend is running",
        time_utc=utc_now(),
        version=APP_VERSION,
    )


@app.get("/health", response_model=HealthResponse)
def health():
    return root()


# =========================
# Auth (MVP)
# =========================
def find_user_by_email(email: str) -> Optional[User]:
    for u in DB["users"]:
        if u["email"].lower() == email.lower():
            return User(**u)
    return None


@app.post("/auth/register", response_model=User)
def register(payload: UserCreate, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)

    if find_user_by_email(payload.email):
        raise HTTPException(status_code=409, detail="Email already registered")

    user_id = new_id("usr", COUNTERS["user"])
    COUNTERS["user"] += 1

    user = User(
        id=user_id,
        full_name=payload.full_name,
        email=payload.email,
        role=payload.role,
        created_at_utc=utc_now(),
    )

    # ⚠️ MVP فقط: نخزن كلمة المرور plain text داخل ذاكرة مؤقتة (غير آمن للإنتاج).
    # للإنتاج: استخدم hashing + DB
    DB["users"].append(
        {
            **user.dict(),
            "_password": payload.password,
        }
    )
    return user


@app.post("/auth/login", response_model=AuthToken)
def login(payload: UserLogin, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)

    for u in DB["users"]:
        if u["email"].lower() == payload.email.lower() and u.get("_password") == payload.password:
            user = User(**{k: v for k, v in u.items() if not k.startswith("_")})
            # MVP token
            token = f"demo-token::{user.id}::{int(datetime.utcnow().timestamp())}"
            return AuthToken(token=token, user=user)

    raise HTTPException(status_code=401, detail="Invalid email or password")


@app.get("/users", response_model=List[User])
def list_users(x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    return [User(**{k: v for k, v in u.items() if not k.startswith("_")}) for u in DB["users"]]


# =========================
# Incidents
# =========================
def get_incident_or_404(incident_id: str) -> Dict[str, Any]:
    for item in DB["incidents"]:
        if item["id"] == incident_id:
            return item
    raise HTTPException(status_code=404, detail="Incident not found")


@app.get("/incidents", response_model=List[Incident])
def list_incidents(
    q: Optional[str] = Query(default=None, description="Search in title/description/location"),
    severity: Optional[str] = Query(default=None, pattern="^(low|medium|high|critical)$"),
    status: Optional[str] = Query(default=None, pattern="^(open|investigating|closed)$"),
    x_api_key: Optional[str] = Header(default=None),
):
    require_api_key(x_api_key)

    items = DB["incidents"]
    if severity:
        items = [i for i in items if i["severity"] == severity]
    if status:
        items = [i for i in items if i["status"] == status]
    if q:
        ql = q.lower()
        def hit(i: Dict[str, Any]) -> bool:
            return (
                ql in (i.get("title") or "").lower()
                or ql in (i.get("description") or "").lower()
                or ql in (i.get("location") or "").lower()
            )
        items = [i for i in items if hit(i)]

    return [Incident(**i) for i in items]


@app.post("/incidents", response_model=Incident)
def create_incident(payload: IncidentCreate, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)

    incident_id = new_id("inc", COUNTERS["incident"])
    COUNTERS["incident"] += 1

    now = utc_now()
    item = Incident(
        id=incident_id,
        created_at_utc=now,
        updated_at_utc=now,
        **payload.model_dump(),
    )

    DB["incidents"].append(item.dict())
    return item


@app.get("/incidents/{incident_id}", response_model=Incident)
def get_incident(incident_id: str, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    item = get_incident_or_404(incident_id)
    return Incident(**item)


class IncidentUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=120)
    location: Optional[str] = Field(default=None, max_length=120)
    description: Optional[str] = Field(default=None, max_length=2000)
    severity: Optional[str] = Field(default=None, pattern="^(low|medium|high|critical)$")
    category: Optional[str] = Field(default=None, max_length=80)
    reported_by: Optional[str] = Field(default=None, max_length=80)
    status: Optional[str] = Field(default=None, pattern="^(open|investigating|closed)$")


@app.patch("/incidents/{incident_id}", response_model=Incident)
def update_incident(incident_id: str, payload: IncidentUpdate, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)

    item = get_incident_or_404(incident_id)
    updates = {k: v for k, v in payload.dict().items() if v is not None}
    item.update(updates)
    item["updated_at_utc"] = utc_now()
    return Incident(**item)


@app.delete("/incidents/{incident_id}", response_model=ApiMessage)
def delete_incident(incident_id: str, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)

    before = len(DB["incidents"])
    DB["incidents"] = [i for i in DB["incidents"] if i["id"] != incident_id]
    if len(DB["incidents"]) == before:
        raise HTTPException(status_code=404, detail="Incident not found")
    return ApiMessage(message="Incident deleted")


# =========================
# Risk Assessments
# =========================
def get_ra_or_404(ra_id: str) -> Dict[str, Any]:
    for item in DB["risk_assessments"]:
        if item["id"] == ra_id:
            return item
    raise HTTPException(status_code=404, detail="Risk assessment not found")


@app.get("/risk-assessments", response_model=List[RiskAssessment])
def list_risk_assessments(
    risk_level: Optional[str] = Query(default=None, pattern="^(low|medium|high|critical)$"),
    status: Optional[str] = Query(default=None, pattern="^(draft|approved|archived)$"),
    x_api_key: Optional[str] = Header(default=None),
):
    require_api_key(x_api_key)

    items = DB["risk_assessments"]
    if risk_level:
        items = [i for i in items if i["risk_level"] == risk_level]
    if status:
        items = [i for i in items if i["status"] == status]
    return [RiskAssessment(**i) for i in items]


@app.post("/risk-assessments", response_model=RiskAssessment)
def create_risk_assessment(payload: RiskAssessmentCreate, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)

    ra_id = new_id("ra", COUNTERS["ra"])
    COUNTERS["ra"] += 1

    now = utc_now()
    item = RiskAssessment(
        id=ra_id,
        created_at_utc=now,
        updated_at_utc=now,
        **payload.model_dump(),
    )
    DB["risk_assessments"].append(item.dict())
    return item


@app.get("/risk-assessments/{ra_id}", response_model=RiskAssessment)
def get_risk_assessment(ra_id: str, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    item = get_ra_or_404(ra_id)
    return RiskAssessment(**item)


class RiskAssessmentUpdate(BaseModel):
    activity: Optional[str] = Field(default=None, min_length=3, max_length=180)
    location: Optional[str] = Field(default=None, max_length=120)
    hazards: Optional[List[str]] = None
    controls: Optional[List[str]] = None
    risk_level: Optional[str] = Field(default=None, pattern="^(low|medium|high|critical)$")
    owner: Optional[str] = Field(default=None, max_length=80)
    status: Optional[str] = Field(default=None, pattern="^(draft|approved|archived)$")


@app.patch("/risk-assessments/{ra_id}", response_model=RiskAssessment)
def update_risk_assessment(ra_id: str, payload: RiskAssessmentUpdate, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    item = get_ra_or_404(ra_id)

    updates = payload.dict()
    updates = {k: v for k, v in updates.items() if v is not None}
    item.update(updates)
    item["updated_at_utc"] = utc_now()
    return RiskAssessment(**item)


@app.delete("/risk-assessments/{ra_id}", response_model=ApiMessage)
def delete_risk_assessment(ra_id: str, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)

    before = len(DB["risk_assessments"])
    DB["risk_assessments"] = [i for i in DB["risk_assessments"] if i["id"] != ra_id]
    if len(DB["risk_assessments"]) == before:
        raise HTTPException(status_code=404, detail="Risk assessment not found")
    return ApiMessage(message="Risk assessment deleted")


# =========================
# Inspections / Checklists
# =========================
def get_inspection_or_404(ins_id: str) -> Dict[str, Any]:
    for item in DB["inspections"]:
        if item["id"] == ins_id:
            return item
    raise HTTPException(status_code=404, detail="Inspection not found")


@app.get("/inspections", response_model=List[Inspection])
def list_inspections(
    site: Optional[str] = Query(default=None),
    overall_status: Optional[str] = Query(default=None, pattern="^(open|closed)$"),
    x_api_key: Optional[str] = Header(default=None),
):
    require_api_key(x_api_key)

    items = DB["inspections"]
    if site:
        sl = site.lower()
        items = [i for i in items if sl in (i.get("site") or "").lower()]
    if overall_status:
        items = [i for i in items if i["overall_status"] == overall_status]
    return [Inspection(**i) for i in items]


@app.post("/inspections", response_model=Inspection)
def create_inspection(payload: InspectionCreate, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)

    ins_id = new_id("ins", COUNTERS["inspection"])
    COUNTERS["inspection"] += 1

    now = utc_now()
    item = Inspection(
        id=ins_id,
        created_at_utc=now,
        updated_at_utc=now,
        date_utc=payload.date_utc or utc_now(),
        **payload.model_dump(exclude={"date_utc"}),
    )
    DB["inspections"].append(item.dict())
    return item


@app.get("/inspections/{inspection_id}", response_model=Inspection)
def get_inspection(inspection_id: str, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    item = get_inspection_or_404(inspection_id)
    return Inspection(**item)


class InspectionUpdate(BaseModel):
    site: Optional[str] = Field(default=None, min_length=2, max_length=120)
    inspector: Optional[str] = Field(default=None, max_length=80)
    overall_status: Optional[str] = Field(default=None, pattern="^(open|closed)$")
    items: Optional[List[InspectionItem]] = None


@app.patch("/inspections/{inspection_id}", response_model=Inspection)
def update_inspection(inspection_id: str, payload: InspectionUpdate, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    item = get_inspection_or_404(inspection_id)

    updates = payload.dict()
    updates = {k: v for k, v in updates.items() if v is not None}
    item.update(updates)
    item["updated_at_utc"] = utc_now()
    return Inspection(**item)


@app.delete("/inspections/{inspection_id}", response_model=ApiMessage)
def delete_inspection(inspection_id: str, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)

    before = len(DB["inspections"])
    DB["inspections"] = [i for i in DB["inspections"] if i["id"] != inspection_id]
    if len(DB["inspections"]) == before:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return ApiMessage(message="Inspection deleted")


# =========================
# Upload (metadata only for MVP)
# =========================
@app.post("/uploads", response_model=UploadMeta)
async def upload_file(
    file: UploadFile = File(...),
    tag: Optional[str] = Query(default=None),
    x_api_key: Optional[str] = Header(default=None),
):
    require_api_key(x_api_key)

    # نقرأ جزء بسيط لحساب الحجم تقريبياً (بدون تخزين)
    content = await file.read()
    size_bytes = len(content)

    up_id = new_id("up", COUNTERS["upload"])
    COUNTERS["upload"] += 1

    meta = UploadMeta(
        id=up_id,
        filename=file.filename,
        content_type=file.content_type,
        size_bytes=size_bytes,
        tag=tag,
        created_at_utc=utc_now(),
    )
    DB["uploads"].append(meta.dict())
    return meta


@app.get("/uploads", response_model=List[UploadMeta])
def list_uploads(x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    return [UploadMeta(**u) for u in DB["uploads"]]

# =========================
# Detection (AI / Camera)
# =========================
@app.post("/detect", response_model=DetectionResult)
async def detect_frame(
    payload: DetectionRequest,
    tracked: bool = Query(False, description="Assign track ids when possible"),
    annotate: bool = Query(False, description="Return annotated JPEG as base64 in raw.annotated_b64"),
    camera_id: Optional[str] = Query(None, description="Optional camera id for tracking context"),
    x_api_key: Optional[str] = Header(default=None),
):
    """
    Detect objects in a frame from the camera.
    - Accepts base64 encoded image data
    - Returns detection results
    """
    require_api_key(x_api_key)
    
    global LAST_DETECTION
    
    try:
        logger.info(f"Received detection request: approx {len(payload.frame_data)} base64 chars")

        # Validate base64 data
        try:
            image_data = base64.b64decode(payload.frame_data)
        except Exception as e:
            logger.error(f"Failed to decode base64 data: {e}")
            raise HTTPException(status_code=400, detail="Invalid base64 data")

        # Call AI engine (modular) in threadpool to avoid blocking the event loop
        conf = float(os.getenv("YOLO_CONF", "0.25"))
        # prefer enhanced API if available
        if hasattr(ai_engine, "detect_frame_enhanced"):
            result = await run_in_threadpool(ai_engine.detect_frame_enhanced, image_data, conf, bool(tracked), bool(annotate), camera_id)
        else:
            result = await run_in_threadpool(ai_engine.detect_frame, image_data, conf)

        det_id = new_id("det", COUNTERS["detection"])
        COUNTERS["detection"] += 1

        timestamp = payload.timestamp or result.get("timestamp") or utc_now()

        detection = DetectionResult(
            id=det_id,
            timestamp=timestamp,
            objects=result.get("objects", []),
            raw_response={
                "model": result.get("model", "baseline"),
            },
            is_valid=True
        )

        DB["detections"].append(detection.dict())
        LAST_DETECTION = detection
        
        # Auto-generate report if risk threshold exceeded
        if detection.objects:
            try:
                risk_threshold = float(os.getenv("REPORT_RISK_THRESHOLD", "0.25"))  # Lower threshold to trigger on moderate detections
                generated_report = report_generator.generate_report(
                    detection_id=detection.id,
                    objects=detection.objects,
                    location=os.getenv("SITE_LOCATION", "Default Site"),
                    timestamp=timestamp
                )
                if generated_report.get("risk_score", 0) >= risk_threshold:
                    with REPORTS_LOCK:
                        REPORTS.append(generated_report)
                    logger.info(f"Auto-generated report: {generated_report['id']} (risk: {generated_report['risk_level']})")
            except Exception as e:
                logger.warning(f"Failed to auto-generate report: {e}")

        logger.info(f"Detection completed: {det_id} - {len(detection.objects)} objects detected")
        return detection

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@app.get("/detections", response_model=List[DetectionResult])
def list_detections(
    limit: int = Query(10, ge=1, le=100),
    x_api_key: Optional[str] = Header(default=None),
):
    """List recent detections"""
    require_api_key(x_api_key)
    items = DB["detections"][-limit:]
    return [DetectionResult(**i) for i in items]


@app.get("/detections/last", response_model=Optional[DetectionResult])
def get_last_detection(x_api_key: Optional[str] = Header(default=None)):
    """Get the most recent detection"""
    require_api_key(x_api_key)
    return LAST_DETECTION


# =========================
# CCTV / Cameras
# =========================


@app.post("/cctv/cameras")
def create_camera(payload: Dict[str, Any], x_api_key: Optional[str] = Header(default=None)):
    """Register a new camera. Body: name, rtsp_url, fps (optional), zones (optional), rules (optional)"""
    require_api_key(x_api_key)
    try:
        cam_id = payload.get("id") or f"cam_{uuid.uuid4().hex[:8]}"
        cam = cctv.Camera(
            id=cam_id,
            name=payload.get("name", cam_id),
            rtsp_url=payload.get("rtsp_url", ""),
            enabled=bool(payload.get("enabled", False)),
            fps=float(payload.get("fps", 2.0)),
            zones=payload.get("zones", []),
            rules=payload.get("rules", {}),
        )
        mgr = cctv.get_manager()
        mgr.create_camera(cam)
        return {"ok": True, "camera": cam.to_dict()}
    except Exception as e:
        logger.error(f"Create camera error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cctv/cameras")
def list_cameras(x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    try:
        mgr = cctv.get_manager()
        return mgr.list_cameras()
    except Exception as e:
        logger.error(f"List cameras error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cctv/cameras/{camera_id}/start")
def start_camera(camera_id: str, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    mgr = cctv.get_manager()
    ok = mgr.start_camera(camera_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Camera not found")
    return {"ok": True, "camera_id": camera_id}


@app.post("/cctv/cameras/{camera_id}/stop")
def stop_camera(camera_id: str, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    mgr = cctv.get_manager()
    ok = mgr.stop_camera(camera_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Camera not found")
    return {"ok": True, "camera_id": camera_id}


@app.get("/cctv/cameras/{camera_id}/status")
def camera_status(camera_id: str, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    mgr = cctv.get_manager()
    status = mgr.status(camera_id)
    if not status.get("exists"):
        raise HTTPException(status_code=404, detail="Camera not found")
    return status


@app.get("/cctv/cameras/{camera_id}/rules")
def get_camera_rules(camera_id: str, x_api_key: Optional[str] = Header(default=None)):
    """Get camera rules/thresholds."""
    require_api_key(x_api_key)
    mgr = cctv.get_manager()
    cams = mgr.list_cameras()
    for c in cams:
        if c.get("id") == camera_id:
            return {"ok": True, "camera_id": camera_id, "rules": c.get("rules", {})}
    raise HTTPException(status_code=404, detail="Camera not found")


@app.post("/cctv/cameras/{camera_id}/rules")
def set_camera_rules(camera_id: str, payload: Dict[str, Any], x_api_key: Optional[str] = Header(default=None)):
    """Set/replace camera rules (JSON)."""
    require_api_key(x_api_key)
    try:
        mgr = cctv.get_manager()
        ok = mgr.update_camera_rules(camera_id, payload)
        if not ok:
            raise HTTPException(status_code=404, detail="Camera not found")
        return {"ok": True, "camera_id": camera_id, "rules": payload}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set camera rules error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cctv/cameras/{camera_id}/detections")
def camera_detections(camera_id: str, limit: int = Query(100, ge=1, le=1000), x_api_key: Optional[str] = Header(default=None)):
    """Query recent detections for a specific camera (SQLite-backed)."""
    require_api_key(x_api_key)
    try:
        items = cctv.query_detections(camera_id=camera_id, limit=limit)
        return {"ok": True, "camera_id": camera_id, "count": len(items), "detections": items}
    except Exception as e:
        logger.error(f"Camera detections query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cctv/detections")
def all_detections(limit: int = Query(200, ge=1, le=2000), x_api_key: Optional[str] = Header(default=None)):
    """Query recent detections across all cameras."""
    require_api_key(x_api_key)
    try:
        items = cctv.query_detections(camera_id=None, limit=limit)
        return {"ok": True, "count": len(items), "detections": items}
    except Exception as e:
        logger.error(f"All detections query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cctv/cameras/{camera_id}/events")
def camera_events(camera_id: str, limit: int = Query(100, ge=1, le=1000), x_api_key: Optional[str] = Header(default=None)):
    """Query recent behavior events/alerts for a camera."""
    require_api_key(x_api_key)
    try:
        items = cctv.query_alerts(camera_id=camera_id, limit=limit)
        return {"ok": True, "camera_id": camera_id, "count": len(items), "events": items}
    except Exception as e:
        logger.error(f"Camera events query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cctv/events")
def all_events(limit: int = Query(200, ge=1, le=2000), x_api_key: Optional[str] = Header(default=None)):
    """Query recent events across all cameras."""
    require_api_key(x_api_key)
    try:
        items = cctv.query_alerts(camera_id=None, limit=limit)
        return {"ok": True, "count": len(items), "events": items}
    except Exception as e:
        logger.error(f"All events query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cctv/cameras/{camera_id}/zones")
def get_camera_zones(camera_id: str, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    mgr = cctv.get_manager()
    cams = mgr.list_cameras()
    for c in cams:
        if c.get("id") == camera_id:
            return {"ok": True, "camera_id": camera_id, "zones": c.get("zones", [])}
    raise HTTPException(status_code=404, detail="Camera not found")


@app.post("/cctv/cameras/{camera_id}/zones")
def add_camera_zone(camera_id: str, payload: Dict[str, Any], x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    try:
        mgr = cctv.get_manager()
        cams = mgr.list_cameras()
        cam = next((x for x in cams if x.get("id") == camera_id), None)
        if not cam:
            raise HTTPException(status_code=404, detail="Camera not found")
        zones = cam.get("zones", []) or []
        zid = payload.get("id") or f"zone_{len(zones)+1}"
        payload["id"] = zid
        zones.append(payload)
        ok = mgr.update_camera_zones(camera_id, zones)
        if not ok:
            raise HTTPException(status_code=500, detail="Failed to update zones")
        return {"ok": True, "camera_id": camera_id, "zone": payload}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add zone error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/cctv/cameras/{camera_id}/zones/{zone_id}")
def update_camera_zone(camera_id: str, zone_id: str, payload: Dict[str, Any], x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    mgr = cctv.get_manager()
    cams = mgr.list_cameras()
    cam = next((x for x in cams if x.get("id") == camera_id), None)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    zones = cam.get("zones", []) or []
    found = False
    for i, z in enumerate(zones):
        if str(z.get("id")) == str(zone_id):
            zones[i] = {**z, **payload, "id": zone_id}
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="Zone not found")
    ok = mgr.update_camera_zones(camera_id, zones)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to update zones")
    return {"ok": True, "camera_id": camera_id, "zone": payload}


@app.delete("/cctv/cameras/{camera_id}/zones/{zone_id}")
def delete_camera_zone(camera_id: str, zone_id: str, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    mgr = cctv.get_manager()
    cams = mgr.list_cameras()
    cam = next((x for x in cams if x.get("id") == camera_id), None)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    zones = cam.get("zones", []) or []
    new_zones = [z for z in zones if str(z.get("id")) != str(zone_id)]
    if len(new_zones) == len(zones):
        raise HTTPException(status_code=404, detail="Zone not found")
    ok = mgr.update_camera_zones(camera_id, new_zones)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to update zones")
    return {"ok": True, "camera_id": camera_id}


@app.post("/cctv/cameras/{camera_id}/webhook")
def set_camera_webhook(camera_id: str, payload: Dict[str, Any], x_api_key: Optional[str] = Header(default=None)):
    """Set webhook_url in camera rules. Body: {"webhook_url": "https://..."} """
    require_api_key(x_api_key)
    try:
        url = payload.get("webhook_url")
        if not url:
            raise HTTPException(status_code=400, detail="Missing webhook_url")
        mgr = cctv.get_manager()
        cams = mgr.list_cameras()
        cam = next((x for x in cams if x.get("id") == camera_id), None)
        if not cam:
            raise HTTPException(status_code=404, detail="Camera not found")
        rules = cam.get("rules", {}) or {}
        rules["webhook_url"] = url
        mgr.update_camera_rules(camera_id, rules)
        return {"ok": True, "camera_id": camera_id, "webhook_url": url}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# Chat (Q&A with Detection Integration)
# =========================
@app.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    x_api_key: Optional[str] = Header(default=None),
):
    """
    Chat endpoint - answer questions, optionally with detection context.
    
    - Ensures exactly ONE response per question
    - Saves to session history
    - Can attach last detection result
    """
    require_api_key(x_api_key)
    
    try:
        logger.info(f"Chat request: {payload.message[:50]}...")
        
        # Get or create session
        session_id = payload.session_id or f"session_{int(datetime.utcnow().timestamp())}"
        if session_id not in DB["chat_sessions"]:
            DB["chat_sessions"][session_id] = []
        
        # Generate response (mock for now)
        # في الإنتاج استدعي خدمة LLM/Chat حقيقية (GPT, Claude, etc.)
        assistant_response = generate_chat_response(
            user_message=payload.message,
            detection_result=payload.detection_result,
            session_history=DB["chat_sessions"][session_id]
        )
        
        chat_id = new_id("chat", COUNTERS["chat_msg"])
        COUNTERS["chat_msg"] += 1
        
        timestamp = utc_now()
        
        # Create response object
        response = ChatResponse(
            id=chat_id,
            session_id=session_id,
            user_message=payload.message,
            assistant_response=assistant_response,
            timestamp=timestamp,
            detection_attached=payload.detection_result is not None,
        )
        
        # Store in session history
        DB["chat_sessions"][session_id].append(response.dict())
        
        logger.info(f"Chat response generated: {chat_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.post("/report", response_model=ApiMessage)
def create_report(payload: Dict[str, Any], x_api_key: Optional[str] = Header(default=None)):
    """Save a quick incident/near-miss report to file-backed storage."""
    require_api_key(x_api_key)
    try:
        report_id = new_id("rpt", COUNTERS.get("report", 1))
        COUNTERS["report"] = COUNTERS.get("report", 1) + 1

        now = utc_now()
        item = {
            "id": report_id,
            "created_at_utc": now,
            **payload,
        }

        with REPORTS_LOCK:
            reports = json.loads(REPORTS_FILE.read_text())
            reports.append(item)
            REPORTS_FILE.write_text(json.dumps(reports, indent=2, ensure_ascii=False))

        logger.info(f"Report saved: {report_id}")
        return ApiMessage(message=f"Report saved: {report_id}")
    except Exception as e:
        logger.error(f"Report save error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save report")


@app.get("/reports", response_model=List[Dict[str, Any]])
def list_reports(x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    try:
        with REPORTS_LOCK:
            reports = json.loads(REPORTS_FILE.read_text())
        return reports
    except Exception as e:
        logger.error(f"List reports error: {e}")
        raise HTTPException(status_code=500, detail="Failed to read reports")


@app.get("/reports/auto", response_model=List[Report])
def list_auto_reports(x_api_key: Optional[str] = Header(default=None)):
    """List auto-generated smart reports from detections."""
    require_api_key(x_api_key)
    with REPORTS_LOCK:
        return REPORTS


@app.get("/reports/export")
def export_reports(
    format: str = Query("json", regex="^(json|csv|pdf|excel)$"),
    x_api_key: Optional[str] = Header(default=None)
):
    """Export all reports in requested format (json, csv, pdf, excel)."""
    require_api_key(x_api_key)
    try:
        with REPORTS_LOCK:
            reports_copy = REPORTS.copy()
        
        if format == "json":
            json_text = export_utils.export_to_json(reports_copy)
            return StreamingResponse(
                iter([json_text]),
                media_type="application/json",
                headers={"Content-Disposition": "attachment; filename=all_reports.json"}
            )
        elif format == "csv":
            csv_text = export_utils.export_to_csv(reports_copy)
            return StreamingResponse(
                iter([csv_text]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=all_reports.csv"}
            )
        elif format == "pdf":
            pdf_bytes = export_utils.export_to_pdf(reports_copy, filename="all_reports.pdf")
            if not pdf_bytes:
                raise HTTPException(status_code=503, detail="PDF export not available (reportlab not installed)")
            return StreamingResponse(
                iter([pdf_bytes]),
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=all_reports.pdf"}
            )
        elif format == "excel":
            excel_bytes = export_utils.export_to_excel(reports_copy, filename="all_reports.xlsx")
            if not excel_bytes:
                raise HTTPException(status_code=503, detail="Excel export not available (openpyxl not installed)")
            return StreamingResponse(
                iter([excel_bytes]),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=all_reports.xlsx"}
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@app.get("/reports/{report_id}", response_model=Report)
def get_report(report_id: str, x_api_key: Optional[str] = Header(default=None)):
    """Get a single auto-generated report by ID."""
    require_api_key(x_api_key)
    with REPORTS_LOCK:
        for r in REPORTS:
            if r.get("id") == report_id:
                return r
    raise HTTPException(status_code=404, detail="Report not found")


def generate_chat_response(
    user_message: str,
    detection_result: Optional[DetectionResult],
    session_history: List[Dict[str, Any]]
) -> str:
    """
    Generate a chat response based on the user message and context.
    
    في الإنتاج:
    - ادعُ خدمة LLM (OpenAI GPT, Anthropic Claude, etc.)
    - استخدم Detection context في system prompt
    - احفظ conversation history
    """
    
    # Prefer a real LLM if configured
    try:
        from . import llm
        det_ctx = detection_result.dict() if detection_result is not None else None
        llm_resp = llm.generate_llm_response(user_message=user_message, detection_context=det_ctx, session_history=session_history)
        if llm_resp:
            return llm_resp
    except Exception:
        # If LLM integration fails, fall back to simple rules below
        pass

    # Fallback simple rule-based response
    if "detection" in user_message.lower():
        return f"Latest detection shows: {len(detection_result.objects) if detection_result else 0} objects detected. Please refer to the detection panel for details."
    if "safety" in user_message.lower():
        return "Safety is our top priority. Always use proper protective equipment and follow safety protocols."
    if "incident" in user_message.lower():
        return "To report an incident, click the 'Create Incident' button and fill in the required details."
    return f"Thank you for your question: '{user_message}'. The system is ready to assist with hazard detection, incident reporting, and risk assessment. How can I help further?"


@app.get("/chat/{session_id}", response_model=List[ChatResponse])
def get_chat_history(
    session_id: str,
    x_api_key: Optional[str] = Header(default=None),
):
    """Get chat history for a specific session"""
    require_api_key(x_api_key)
    
    if session_id not in DB["chat_sessions"]:
        logger.warning(f"Chat session not found: {session_id}")
        return []
    
    return [ChatResponse(**msg) for msg in DB["chat_sessions"][session_id]]


@app.delete("/chat/{session_id}", response_model=ApiMessage)
def clear_chat_session(
    session_id: str,
    x_api_key: Optional[str] = Header(default=None),
):
    """Clear all messages in a chat session"""
    require_api_key(x_api_key)
    
    if session_id in DB["chat_sessions"]:
        del DB["chat_sessions"][session_id]
        logger.info(f"Chat session cleared: {session_id}")
    
    return ApiMessage(message=f"Chat session {session_id} cleared")