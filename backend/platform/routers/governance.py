import json
from datetime import datetime, timezone

from fastapi import APIRouter, Request
from pydantic import BaseModel

from backend.platform.db import get_conn
from backend.platform.responses import ok

router = APIRouter(prefix="/governance", tags=["governance"])

RBAC = {
    "admin": ["*"],
    "hse": ["incidents", "observations", "reports", "environment", "training"],
    "supervisor": ["observations", "ptw", "behavior_analytics"],
    "viewer": ["read_only"],
}


class PolicyIn(BaseModel):
    site: str
    name: str
    description: str


class ChecklistIn(BaseModel):
    site: str
    item: str
    status: str = "open"
    owner: str
    due_date: str


@router.get("/roles")
def roles(request: Request):
    return ok({"roles": RBAC}, request.state.request_id)


@router.post("/policies")
def create_policy(body: PolicyIn, request: Request):
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO policies(site,name,description,created_at) VALUES(?,?,?,?)",
            (body.site, body.name, body.description, now),
        )
        conn.execute(
            "INSERT INTO audit_logs(actor,action,entity,entity_id,details_json,created_at) VALUES(?,?,?,?,?,?)",
            (
                "system",
                "create",
                "policy",
                str(cur.lastrowid),
                json.dumps(body.model_dump()),
                now,
            ),
        )
        conn.commit()
    return ok({"id": cur.lastrowid}, request.state.request_id)


@router.get("/audit-logs")
def audit_logs(request: Request):
    with get_conn() as conn:
        rows = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM audit_logs ORDER BY id DESC LIMIT 100"
            ).fetchall()
        ]
    return ok({"items": rows}, request.state.request_id)


@router.post("/compliance-checklist")
def create_checklist(body: ChecklistIn, request: Request):
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO compliance_checklists(site,item,status,owner,due_date,created_at) VALUES(?,?,?,?,?,?)",
            (body.site, body.item, body.status, body.owner, body.due_date, now),
        )
        conn.commit()
    return ok({"id": cur.lastrowid}, request.state.request_id)


@router.get("/compliance-checklist")
def list_checklist(request: Request, site: str | None = None):
    q = "SELECT * FROM compliance_checklists"
    params = []
    if site:
        q += " WHERE site=?"
        params.append(site)
    with get_conn() as conn:
        rows = [dict(r) for r in conn.execute(q, tuple(params)).fetchall()]
    return ok({"items": rows}, request.state.request_id)
