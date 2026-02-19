from fastapi import APIRouter, Request

from backend.platform.db import get_conn
from backend.platform.responses import ok

router = APIRouter(prefix="/exclusive", tags=["exclusive"])


@router.get("/smart-recommendations")
def smart_recommendations(request: Request):
    with get_conn() as conn:
        high = conn.execute(
            "SELECT COUNT(*) c FROM incidents WHERE risk_score >= 15"
        ).fetchone()["c"]
        env = conn.execute(
            "SELECT COUNT(*) c FROM environment_measurements WHERE metric='noise' AND value>85"
        ).fetchone()["c"]
    recs = []
    if high:
        recs.append("Run immediate supervisor coaching on high-risk tasks")
    if env:
        recs.append("Deploy engineering noise controls and hearing protection checks")
    if not recs:
        recs.append("Maintain current controls and run proactive toolbox talk")
    return ok({"recommendations": recs}, request.state.request_id)


@router.get("/safety-score")
def safety_score(request: Request):
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT department,
            SUM(CASE WHEN category IN ('unsafe act','at-risk behavior') THEN 1 ELSE 0 END) AS risky_obs,
            COUNT(*) AS total_obs
            FROM observations
            GROUP BY department
            """
        ).fetchall()
        inc = conn.execute("SELECT COUNT(*) c FROM incidents").fetchone()["c"]
    scores = []
    for r in rows:
        behavior_penalty = (r["risky_obs"] / max(1, r["total_obs"])) * 40
        incident_penalty = min(30, inc * 2)
        score = max(0, 100 - behavior_penalty - incident_penalty)
        scores.append({"department": r["department"], "score": round(score, 2)})
    return ok({"safety_scores": scores}, request.state.request_id)


@router.get("/reports/json")
def structured_report(request: Request):
    with get_conn() as conn:
        incidents = [
            dict(r)
            for r in conn.execute(
                "SELECT id,title,risk_score,status FROM incidents ORDER BY id DESC LIMIT 20"
            ).fetchall()
        ]
    return ok(
        {"report_type": "structured_json", "incidents": incidents},
        request.state.request_id,
    )
