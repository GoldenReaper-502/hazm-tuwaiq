from datetime import date
from fastapi import APIRouter, Request
from pydantic import BaseModel
from backend.platform.responses import ok
from backend.platform.db import get_conn

router = APIRouter(prefix="/training", tags=["training"])


class TrainingIn(BaseModel):
    employee_name: str
    course_name: str
    expires_at: str
    completed_at: str


@router.post("")
def add_training(body: TrainingIn, request: Request):
    with get_conn() as conn:
        cur = conn.execute("INSERT INTO trainings(employee_name,course_name,expires_at,completed_at,compliant) VALUES(?,?,?,?,1)", (body.employee_name, body.course_name, body.expires_at, body.completed_at))
        conn.commit()
    return ok({"id": cur.lastrowid}, request.state.trace_id)


@router.get("/compliance")
def compliance(request: Request):
    today = str(date.today())
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) c FROM trainings").fetchone()["c"]
        expiring = conn.execute("SELECT COUNT(*) c FROM trainings WHERE expires_at <= date(?, '+30 day')", (today,)).fetchone()["c"]
    return ok({"total_records": total, "expiring_within_30_days": expiring}, request.state.trace_id)
