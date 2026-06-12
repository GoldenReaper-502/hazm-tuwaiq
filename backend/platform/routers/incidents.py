import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from backend.platform.auth import require_any_role
from backend.platform.db import get_conn
from backend.platform.responses import fail, ok
from backend.platform.services.audit_service import audit_event
from backend.platform.utils import paginate_sql

router = APIRouter(prefix="/incidents", tags=["incidents"])


class IncidentIn(BaseModel):
    title: str
    description: str = ""
    site: str = "HQ"
    department: str = "General"
    severity: int = Field(ge=1, le=5)
    likelihood: int = Field(ge=1, le=5)
    status: str = "open"
    evidence: list[dict] = []
    corrective_actions: list[dict] = []
    due_date: str | None = None


class ActionIn(BaseModel):
    action_text: str
    owner: str
    due_date: str


class RcaIn(BaseModel):
    why1: str = ""
    why2: str = ""
    why3: str = ""
    why4: str = ""
    why5: str = ""
    category: str = "process"


@router.get("")
def list_incidents(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    site: str | None = None,
    sort_by: str = "id",
    sort_dir: str = "desc",
):
    q = "SELECT * FROM incidents WHERE 1=1"
    params = []
    if status:
        q += " AND status=?"
        params.append(status)
    if site:
        q += " AND site=?"
        params.append(site)
    q = paginate_sql(q, page, page_size, sort_by, sort_dir)
    with get_conn() as conn:
        rows = [dict(r) for r in conn.execute(q, tuple(params)).fetchall()]
    return ok(rows, request.state.request_id)


@router.post("")
def create_incident(
    body: IncidentIn,
    request: Request,
    _=Depends(require_any_role(["admin", "safety_officer", "inspector", "supervisor", "hse"])),
):
    risk_score = body.severity * body.likelihood
    escalation_level = 2 if risk_score >= 16 else (1 if risk_score >= 9 else 0)
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO incidents(title,description,site,department,severity,likelihood,risk_score,status,evidence_json,corrective_actions_json,due_date,escalation_level,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                body.title,
                body.description,
                body.site,
                body.department,
                body.severity,
                body.likelihood,
                risk_score,
                body.status,
                json.dumps(body.evidence),
                json.dumps(body.corrective_actions),
                body.due_date,
                escalation_level,
                now,
                now,
            ),
        )
        conn.commit()
    audit_event("system", "create", "incident", str(cur.lastrowid), body.model_dump())
    return ok(
        {
            "id": cur.lastrowid,
            "risk_score": risk_score,
            "escalation_level": escalation_level,
        },
        request.state.request_id,
    )


@router.get("/analytics/summary")
def incidents_summary(request: Request):
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) c FROM incidents").fetchone()["c"]
        open_i = conn.execute(
            "SELECT COUNT(*) c FROM incidents WHERE status!='closed'"
        ).fetchone()["c"]
        high = conn.execute(
            "SELECT COUNT(*) c FROM incidents WHERE risk_score>=12"
        ).fetchone()["c"]
    return ok(
        {"total": total, "open": open_i, "high_risk": high}, request.state.request_id
    )


@router.get("/{incident_id}")
def get_incident(incident_id: int, request: Request):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM incidents WHERE id=?", (incident_id,)
        ).fetchone()
    if not row:
        raise HTTPException(
            status_code=404,
            detail=fail(
                "INCIDENT_NOT_FOUND", "Incident not found", request.state.request_id
            ),
        )
    return ok(dict(row), request.state.request_id)


@router.patch("/{incident_id}")
def patch_incident(
    incident_id: int,
    body: IncidentIn,
    request: Request,
    _=Depends(require_any_role(["admin", "safety_officer", "inspector", "hse"])),
):
    risk_score = body.severity * body.likelihood
    escalation_level = 2 if risk_score >= 16 else (1 if risk_score >= 9 else 0)
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE incidents SET title=?,description=?,site=?,department=?,severity=?,likelihood=?,risk_score=?,status=?,evidence_json=?,corrective_actions_json=?,due_date=?,escalation_level=?,updated_at=? WHERE id=?",
            (
                body.title,
                body.description,
                body.site,
                body.department,
                body.severity,
                body.likelihood,
                risk_score,
                body.status,
                json.dumps(body.evidence),
                json.dumps(body.corrective_actions),
                body.due_date,
                escalation_level,
                now,
                incident_id,
            ),
        )
        conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=fail(
                "INCIDENT_NOT_FOUND", "Incident not found", request.state.request_id
            ),
        )
    audit_event("system", "update", "incident", str(incident_id), body.model_dump())
    return ok({"updated": True, "risk_score": risk_score}, request.state.request_id)


@router.delete("/{incident_id}")
def delete_incident(
    incident_id: int, request: Request, _=Depends(require_any_role(["admin"]))
):
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM incidents WHERE id=?", (incident_id,))
        conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=fail(
                "INCIDENT_NOT_FOUND", "Incident not found", request.state.request_id
            ),
        )
    audit_event("system", "delete", "incident", str(incident_id), {})
    return ok({"deleted": True}, request.state.request_id)


@router.post("/{incident_id}/actions")
def add_action(incident_id: int, body: ActionIn, request: Request):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO incident_actions(incident_id,action_text,owner,due_date,status,created_at) VALUES(?,?,?,?,?,datetime('now'))",
            (incident_id, body.action_text, body.owner, body.due_date, "open"),
        )
        conn.commit()
    audit_event(
        "system", "create_action", "incident", str(incident_id), body.model_dump()
    )
    return ok({"action_id": cur.lastrowid}, request.state.request_id)


@router.post("/{incident_id}/rca")
def set_rca(incident_id: int, body: RcaIn, request: Request):
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE incidents SET evidence_json=? WHERE id=?",
            (json.dumps(body.model_dump()), incident_id),
        )
        conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=fail(
                "INCIDENT_NOT_FOUND", "Incident not found", request.state.request_id
            ),
        )
    audit_event("system", "set_rca", "incident", str(incident_id), body.model_dump())
    return ok({"rca_saved": True}, request.state.request_id)


@router.get("/analytics")
def incidents_analytics(request: Request):
    with get_conn() as conn:
        by_status = [
            dict(r)
            for r in conn.execute(
                "SELECT status, COUNT(*) c FROM incidents GROUP BY status"
            ).fetchall()
        ]
        top_sites = [
            dict(r)
            for r in conn.execute(
                "SELECT site, COUNT(*) c FROM incidents GROUP BY site ORDER BY c DESC LIMIT 5"
            ).fetchall()
        ]
    return ok(
        {"by_status": by_status, "top_sites": top_sites}, request.state.request_id
    )
