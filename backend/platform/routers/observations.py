from datetime import datetime, timezone, date
from fastapi import APIRouter, Request
from pydantic import BaseModel
from backend.platform.responses import ok
from backend.platform.db import get_conn

router = APIRouter(prefix="/observations", tags=["observations"])


class ObservationIn(BaseModel):
    category: str  # safe act / unsafe act / at-risk behavior
    location: str
    site: str = "HQ"
    observed_at: str
    department: str
    corrective_action: str
    due_date: str
    responsible_person: str


@router.post("")
def create_observation(body: ObservationIn, request: Request):
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO observations(category,location,site,observed_at,department,corrective_action,due_date,responsible_person,created_at)
               VALUES(?,?,?,?,?,?,?,?,?)""",
            (body.category, body.location, body.site, body.observed_at, body.department, body.corrective_action, body.due_date, body.responsible_person, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    return ok({"id": cur.lastrowid}, request.state.request_id)


@router.get("/kpis")
def observation_kpis(request: Request):
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) c FROM observations").fetchone()["c"]
        closed = conn.execute("SELECT COUNT(*) c FROM observations WHERE closed=1").fetchone()["c"]
        today = str(date.today())
        overdue = conn.execute("SELECT COUNT(*) c FROM observations WHERE closed=0 AND due_date < ?", (today,)).fetchone()["c"]
    closure = (closed / total * 100) if total else 0
    return ok({"total": total, "closed": closed, "overdue": overdue, "closure_rate": round(closure, 2)}, request.state.request_id)


@router.get("/trends")
def observation_trends(request: Request):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT department, COUNT(*) total, SUM(CASE WHEN category='unsafe act' OR category='at-risk behavior' THEN 1 ELSE 0 END) unsafe_count FROM observations GROUP BY department"
        ).fetchall()
    trends = []
    for r in rows:
        score = max(0, 100 - (r["unsafe_count"] / max(1, r["total"]) * 100))
        trends.append({"department": r["department"], "unsafe_rate": round(r["unsafe_count"] / max(1, r["total"]), 2), "behavior_score": round(score, 2)})
    return ok({"trends": trends}, request.state.request_id)
