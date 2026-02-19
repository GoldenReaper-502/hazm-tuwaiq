import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Request

from backend.platform.db import get_conn
from backend.platform.responses import ok

router = APIRouter(prefix="/reports", tags=["reports"])


def _summary(period_days: int):
    since = (datetime.now(timezone.utc) - timedelta(days=period_days)).isoformat()
    with get_conn() as conn:
        incidents = conn.execute(
            "SELECT COUNT(*) c FROM incidents WHERE created_at >= ?", (since,)
        ).fetchone()["c"]
        observations = conn.execute(
            "SELECT COUNT(*) c FROM observations WHERE created_at >= ?", (since,)
        ).fetchone()["c"]
        inspections = conn.execute(
            "SELECT COUNT(*) c FROM inspections WHERE created_at >= ?", (since,)
        ).fetchone()["c"]
        alerts = conn.execute(
            "SELECT COUNT(*) c FROM alert_events WHERE created_at >= ?", (since,)
        ).fetchone()["c"]
    return {
        "since": since,
        "incidents": incidents,
        "observations": observations,
        "inspections": inspections,
        "alerts": alerts,
    }


def _store_snapshot(report_type: str, payload: dict):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO reports_snapshots(report_type,payload_json,created_at) VALUES(?,?,datetime('now'))",
            (report_type, json.dumps(payload)),
        )
        conn.commit()


@router.get("/daily")
def daily(request: Request):
    payload = _summary(1)
    _store_snapshot("daily", payload)
    return ok(payload, request.state.request_id)


@router.get("/weekly")
def weekly(request: Request):
    payload = _summary(7)
    _store_snapshot("weekly", payload)
    return ok(payload, request.state.request_id)


@router.get("/monthly")
def monthly(request: Request):
    payload = _summary(30)
    _store_snapshot("monthly", payload)
    return ok(payload, request.state.request_id)


@router.get("/export")
def export_report(request: Request, type: str = "weekly", format: str = "json"):
    payload = _summary(7 if type == "weekly" else (1 if type == "daily" else 30))
    if format == "csv":
        csv_text = "metric,value\n" + "\n".join(
            [f"{k},{v}" for k, v in payload.items()]
        )
        return ok(
            {
                "filename": f"{type}_report_{datetime.now(timezone.utc).date()}.csv",
                "content": csv_text,
            },
            request.state.request_id,
        )
    return ok(
        {
            "filename": f"{type}_report_{datetime.now(timezone.utc).date()}.json",
            "report": payload,
        },
        request.state.request_id,
    )
