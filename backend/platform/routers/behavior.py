from fastapi import APIRouter, Request
from pydantic import BaseModel
from backend.platform.responses import ok
from backend.platform.db import get_conn

router = APIRouter(prefix="/behavior", tags=["behavior"])


class ObservationIn(BaseModel):
    category: str
    site: str
    department: str
    note: str = ""


@router.post("/observations")
def create_behavior_observation(body: ObservationIn, request: Request):
    with get_conn() as conn:
        conn.execute("INSERT INTO observations(category,location,site,observed_at,department,corrective_action,due_date,responsible_person,closed,created_at) VALUES(?,?,?,?,?,?,?,?,?,datetime('now'))",
                     (body.category, "Behavior", body.site, "", body.department, body.note, "2030-01-01", "system", 0))
        conn.commit()
    return ok({"created": True}, request.state.request_id)


@router.get("/analytics")
def behavior_analytics(request: Request):
    with get_conn() as conn:
        rows = conn.execute("SELECT department, COUNT(*) total, SUM(CASE WHEN category IN ('unsafe act','at-risk behavior','distraction','rushing','unsafe posture') THEN 1 ELSE 0 END) unsafe_count FROM observations GROUP BY department").fetchall()
    data = []
    for r in rows:
        safe = max(0, 100 - (r["unsafe_count"] / max(1, r["total"]) * 100))
        data.append({"department": r["department"], "safety_culture_score": round(safe, 2), "leading_indicators": r["total"], "lagging_indicators": r["unsafe_count"]})
    return ok(data, request.state.request_id)


@router.get("/score")
def behavior_score(request: Request):
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) c FROM observations").fetchone()["c"]
        unsafe = conn.execute("SELECT COUNT(*) c FROM observations WHERE category IN ('unsafe act','at-risk behavior','distraction','rushing','unsafe posture')").fetchone()["c"]
    score = max(0, 100 - (unsafe / max(1, total) * 100))
    return ok({"weekly_safety_culture_score": round(score, 2)}, request.state.request_id)
