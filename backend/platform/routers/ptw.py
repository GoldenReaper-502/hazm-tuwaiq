import json
from datetime import datetime, timezone
from fastapi import APIRouter, Request
from pydantic import BaseModel
from backend.platform.responses import ok
from backend.platform.db import get_conn

router = APIRouter(prefix="/ptw", tags=["ptw"])


class PTWIn(BaseModel):
    work_type: str
    checklist: list[dict]
    status: str = "submitted"
    approver: str = ""


@router.post("")
def create_ptw(body: PTWIn, request: Request):
    with get_conn() as conn:
        cur = conn.execute("INSERT INTO ptw_permits(work_type,checklist_json,status,approver,created_at) VALUES(?,?,?,?,?)", (body.work_type, json.dumps(body.checklist), body.status, body.approver, datetime.now(timezone.utc).isoformat()))
        conn.commit()
    return ok({"id": cur.lastrowid, "workflow": ["submitted", "approved", "closed"]}, request.state.trace_id)


@router.get("/dashboard")
def ptw_dashboard(request: Request):
    with get_conn() as conn:
        rows = conn.execute("SELECT status, COUNT(*) c FROM ptw_permits GROUP BY status").fetchall()
    return ok({"status_breakdown": [dict(r) for r in rows]}, request.state.trace_id)
