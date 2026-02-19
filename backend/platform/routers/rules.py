import json
from fastapi import APIRouter, Request
from pydantic import BaseModel
from backend.platform.responses import ok
from backend.platform.db import get_conn

router = APIRouter(prefix="/rules", tags=["rules"])


class RuleIn(BaseModel):
    name: str
    condition_expr: str
    action_expr: str
    enabled: int = 1


@router.get("")
def list_rules(request: Request):
    with get_conn() as conn:
        rows = [dict(r) for r in conn.execute("SELECT * FROM rules ORDER BY id DESC").fetchall()]
    return ok(rows, request.state.request_id)


@router.post("")
def create_rule(body: RuleIn, request: Request):
    with get_conn() as conn:
        cur = conn.execute("INSERT INTO rules(name,condition_expr,action_expr,enabled,created_at) VALUES(?,?,?,?,datetime('now'))", (body.name, body.condition_expr, body.action_expr, body.enabled))
        conn.commit()
    return ok({"id": cur.lastrowid}, request.state.request_id)


@router.post("/run")
def run_rules(request: Request):
    events = []
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM rules WHERE enabled=1").fetchall()
        dust = conn.execute("SELECT COUNT(*) c FROM environment_measurements WHERE metric='dust' AND exceeded=1").fetchone()["c"]
        offline = conn.execute("SELECT COUNT(*) c FROM cameras WHERE status='offline'").fetchone()["c"]
        overdue = conn.execute("SELECT COUNT(*) c FROM incident_actions WHERE status!='closed' AND due_date < date('now','-7 day')").fetchone()["c"]
        for r in rows:
            triggered = dust > 0 or offline > 0 or overdue > 0
            status = "triggered" if triggered else "skipped"
            payload = {"dust_exceeded": dust, "offline_cameras": offline, "overdue_actions_7d": overdue}
            conn.execute("INSERT INTO rule_events(rule_id,status,payload_json,created_at) VALUES(?,?,?,datetime('now'))", (r["id"], status, json.dumps(payload)))
            if triggered:
                conn.execute("INSERT INTO notifications(channel,title,message,status,created_at) VALUES(?,?,?,?,datetime('now'))", ("in_app", f"Rule: {r['name']}", "Rule triggered", "unread"))
            events.append({"rule_id": r["id"], "status": status, "payload": payload})
        conn.commit()
    return ok(events, request.state.request_id)


@router.get("/events")
def list_rule_events(request: Request):
    with get_conn() as conn:
        rows = [dict(r) for r in conn.execute("SELECT * FROM rule_events ORDER BY id DESC LIMIT 200").fetchall()]
    return ok(rows, request.state.request_id)
