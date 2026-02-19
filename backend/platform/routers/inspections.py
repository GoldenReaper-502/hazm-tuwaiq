import json

from fastapi import APIRouter, Request
from pydantic import BaseModel

from backend.platform.db import get_conn
from backend.platform.responses import ok

router = APIRouter(tags=["inspections"])


class TemplateIn(BaseModel):
    name: str
    checklist: list[str]


class InspectionIn(BaseModel):
    site: str
    department: str
    template_id: int
    scheduled_date: str


class SubmitIn(BaseModel):
    result: dict
    nonconformities: list[dict] = []


@router.get("/inspection-templates")
def list_templates(request: Request):
    with get_conn() as conn:
        rows = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM inspection_templates ORDER BY id DESC"
            ).fetchall()
        ]
    return ok(rows, request.state.request_id)


@router.post("/inspection-templates")
def create_template(body: TemplateIn, request: Request):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO inspection_templates(name,checklist_json,created_at) VALUES(?,?,datetime('now'))",
            (body.name, json.dumps(body.checklist)),
        )
        conn.commit()
    return ok({"id": cur.lastrowid}, request.state.request_id)


@router.get("/inspections")
def list_inspections(request: Request):
    with get_conn() as conn:
        rows = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM inspections ORDER BY id DESC"
            ).fetchall()
        ]
    return ok(rows, request.state.request_id)


@router.post("/inspections")
def create_inspection(body: InspectionIn, request: Request):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO inspections(site,department,template_id,scheduled_date,status,result_json,nonconformities_json,created_at) VALUES(?,?,?,?,?,?,?,datetime('now'))",
            (
                body.site,
                body.department,
                body.template_id,
                body.scheduled_date,
                "scheduled",
                "{}",
                "[]",
            ),
        )
        conn.commit()
    return ok({"id": cur.lastrowid}, request.state.request_id)


@router.post("/inspections/{inspection_id}/submit")
def submit_inspection(inspection_id: int, body: SubmitIn, request: Request):
    with get_conn() as conn:
        conn.execute(
            "UPDATE inspections SET status='submitted', result_json=?, nonconformities_json=? WHERE id=?",
            (json.dumps(body.result), json.dumps(body.nonconformities), inspection_id),
        )
        conn.commit()
    return ok({"submitted": True}, request.state.request_id)


@router.get("/inspections/overdue")
def overdue_inspections(request: Request):
    with get_conn() as conn:
        rows = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM inspections WHERE status='scheduled' AND scheduled_date < date('now')"
            ).fetchall()
        ]
    return ok(rows, request.state.request_id)
