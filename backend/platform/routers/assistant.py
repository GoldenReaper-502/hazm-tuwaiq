from datetime import datetime, timezone
from fastapi import APIRouter, Request
from pydantic import BaseModel
from backend.platform.responses import ok
from backend.platform.db import get_conn

router = APIRouter(prefix="/assistant", tags=["assistant"])


class ChatIn(BaseModel):
    message: str


@router.post("/chat")
def chat(body: ChatIn, request: Request):
    with get_conn() as conn:
        incidents = conn.execute("SELECT COUNT(*) c FROM incidents WHERE status!='closed'").fetchone()["c"]
        overdue = conn.execute("SELECT COUNT(*) c FROM incident_actions WHERE status!='closed' AND due_date < date('now')").fetchone()["c"]
    answer = f"تم تحليل البيانات: الحوادث المفتوحة={incidents}، الإجراءات المتأخرة={overdue}. التوصية: تكثيف الإشراف الميداني وجلسات toolbox talk."
    return ok({"reply": answer, "recommendations": ["Toolbox talk", "Supervisor coaching", "PPE audit"]}, request.state.request_id)


@router.get("/daily-brief")
def daily_brief(request: Request):
    with get_conn() as conn:
        inc = conn.execute("SELECT COUNT(*) c FROM incidents WHERE date(created_at)=date('now')").fetchone()["c"]
        obs = conn.execute("SELECT COUNT(*) c FROM observations WHERE date(created_at)=date('now')").fetchone()["c"]
        alerts = conn.execute("SELECT COUNT(*) c FROM alert_events WHERE date(created_at)=date('now')").fetchone()["c"]
    return ok({"date": datetime.now(timezone.utc).date().isoformat(), "summary": {"incidents_today": inc, "observations_today": obs, "alerts_today": alerts}}, request.state.request_id)


@router.get("/recommendations")
def recommendations(request: Request):
    return ok({"items": ["Inspect high-risk work areas", "Close overdue corrective actions", "Review environmental exceedances"]}, request.state.request_id)


@router.post("/generate-report")
def generate_report(request: Request, payload: dict):
    topic = payload.get("topic", "weekly safety")
    return ok({"title": f"{topic} report", "sections": ["Summary", "Risks", "Actions", "Recommendations"]}, request.state.request_id)
