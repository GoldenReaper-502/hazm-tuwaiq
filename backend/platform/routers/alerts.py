import json
from datetime import datetime, timezone, date
from fastapi import APIRouter, Request
from backend.platform.responses import ok
from backend.platform.db import get_conn

router = APIRouter(prefix="/alerts", tags=["alerts"])


def emit_alert(rule_name: str, severity: str, payload: dict, channel: str):
    with get_conn() as conn:
        conn.execute("INSERT INTO alert_events(rule_name,severity,payload_json,channel,created_at) VALUES(?,?,?,?,?)", (rule_name, severity, json.dumps(payload), channel, datetime.now(timezone.utc).isoformat()))
        conn.commit()


@router.post("/evaluate")
def evaluate(request: Request):
    today = str(date.today())
    triggered = []
    with get_conn() as conn:
        overdue = conn.execute("SELECT COUNT(*) c FROM observations WHERE closed=0 AND due_date < ?", (today,)).fetchone()["c"]
        high_risk = conn.execute("SELECT COUNT(*) c FROM incidents WHERE risk_score >= 16").fetchone()["c"]
        env_breach = conn.execute("SELECT COUNT(*) c FROM environment_measurements WHERE metric='PM2.5' AND value>35").fetchone()["c"]
    if overdue > 5:
        triggered.append({"rule": "overdue_actions", "value": overdue})
    if high_risk > 2:
        triggered.append({"rule": "high_risk_repeat", "value": high_risk})
    if env_breach > 0:
        triggered.append({"rule": "environment_threshold", "value": env_breach})

    for t in triggered:
        for ch in ["in_app", "email_stub", "webhook_stub"]:
            emit_alert(t["rule"], "high", t, ch)
    return ok({"triggered": triggered, "channels": ["in_app", "email_stub", "webhook_stub"]}, request.state.trace_id)
