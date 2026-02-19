from fastapi import APIRouter, Request
from backend.platform.responses import ok
from backend.platform.db import get_conn

router = APIRouter(prefix="/predictive", tags=["predictive"])


@router.get("/hotspots")
def hotspots(request: Request):
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT i.site,
                   COUNT(i.id) incidents,
                   SUM(CASE WHEN i.risk_score >= 12 THEN 1 ELSE 0 END) high_risk,
                   COALESCE((SELECT COUNT(*) FROM observations o WHERE o.site=i.site AND (o.category='unsafe act' OR o.category='at-risk behavior')),0) unsafe_obs,
                   COALESCE((SELECT COUNT(*) FROM environment_measurements e WHERE e.site=i.site AND e.exceeded=1),0) env_exceed
            FROM incidents i
            GROUP BY i.site
            """
        ).fetchall()

    ranked = []
    for r in rows:
        score = r["incidents"] * 2 + r["high_risk"] * 3 + r["unsafe_obs"] + r["env_exceed"] * 2
        ranked.append({"site": r["site"], "hotspot_score": score})

    ranked.sort(key=lambda x: x["hotspot_score"], reverse=True)
    interventions = [
        "Targeted toolbox talks",
        "Supervisor coaching for at-risk teams",
        "Engineering controls in hotspot zones",
        "Short-interval environmental monitoring",
    ]
    return ok({"top_5_hotspots": ranked[:5], "recommended_interventions": interventions}, request.state.request_id)
