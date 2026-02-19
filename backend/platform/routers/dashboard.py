from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Request

from backend.platform.db import get_conn
from backend.platform.responses import ok

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
def overview(request: Request):
    since_24 = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    with get_conn() as conn:
        active_cams = conn.execute(
            "SELECT COUNT(*) c FROM cameras WHERE status='online'"
        ).fetchone()["c"]
        all_cams = conn.execute("SELECT COUNT(*) c FROM cameras").fetchone()["c"]
        incidents_open = conn.execute(
            "SELECT COUNT(*) c FROM incidents WHERE status!='closed'"
        ).fetchone()["c"]
        overdue_actions = conn.execute(
            "SELECT COUNT(*) c FROM incident_actions WHERE status!='closed' AND due_date < date('now')"
        ).fetchone()["c"]
        last_incidents = [
            dict(r)
            for r in conn.execute(
                "SELECT id,title,risk_score,status,created_at FROM incidents ORDER BY id DESC LIMIT 10"
            ).fetchall()
        ]
        last_detections = [
            dict(r)
            for r in conn.execute(
                "SELECT id,event_type,payload_json,created_at FROM vision_events ORDER BY id DESC LIMIT 10"
            ).fetchall()
        ]
        detections_today = conn.execute(
            "SELECT COUNT(*) c FROM vision_events WHERE date(created_at)=date('now')"
        ).fetchone()["c"]
        avg_risk = (
            conn.execute("SELECT ROUND(AVG(risk_score),2) v FROM incidents").fetchone()[
                "v"
            ]
            or 0
        )
        env_ex = conn.execute(
            "SELECT COUNT(*) c FROM environment_measurements WHERE exceeded=1 AND measured_at >= ?",
            (since_24,),
        ).fetchone()["c"]

    return ok(
        {
            "connected_status": "connected",
            "kpis": {
                "incidents_today": len(
                    [
                        x
                        for x in last_incidents
                        if (x.get("created_at") or "")[:10]
                        == datetime.now(timezone.utc).date().isoformat()
                    ]
                ),
                "open_actions": overdue_actions,
                "cameras_online": active_cams,
                "detections_today": detections_today,
                "risk_score_avg": avg_risk,
            },
            "counters": {
                "cameras_total": all_cams,
                "cameras_active": active_cams,
                "incidents_open": incidents_open,
                "actions_overdue": overdue_actions,
            },
            "last_incidents": last_incidents,
            "last_detections": last_detections,
            "environment_exceedances_last_24h": env_ex,
        },
        request.state.request_id,
    )


@router.get("/trends")
def trends(request: Request, days: int = 7):
    with get_conn() as conn:
        rows = []
        for i in range(days - 1, -1, -1):
            day_expr = f"date('now','-{i} day')"
            inc = conn.execute(
                f"SELECT COUNT(*) c FROM incidents WHERE date(created_at)={day_expr}"
            ).fetchone()["c"]
            det = conn.execute(
                f"SELECT COUNT(*) c FROM vision_events WHERE date(created_at)={day_expr}"
            ).fetchone()["c"]
            alerts = conn.execute(
                f"SELECT COUNT(*) c FROM alert_events WHERE date(created_at)={day_expr}"
            ).fetchone()["c"]
            rows.append(
                {"day_offset": i, "incidents": inc, "detections": det, "alerts": alerts}
            )
    return ok(rows, request.state.request_id)


@router.get("/activity")
def activity(request: Request):
    with get_conn() as conn:
        feed = [
            dict(r)
            for r in conn.execute(
                "SELECT 'incident' as type, title as title, created_at as ts FROM incidents UNION ALL SELECT 'vision' as type, event_type as title, created_at as ts FROM vision_events UNION ALL SELECT 'alert' as type, rule_name as title, created_at as ts FROM alert_events ORDER BY ts DESC LIMIT 30"
            ).fetchall()
        ]
    return ok(feed, request.state.request_id)
