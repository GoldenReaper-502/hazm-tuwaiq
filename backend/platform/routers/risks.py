from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from backend.platform.db import get_conn
from backend.platform.responses import ok

router = APIRouter(prefix="/risks", tags=["risks"])


class RiskIn(BaseModel):
    hazard: str
    site: str
    department: str
    controls: str = ""
    severity: int = Field(ge=1, le=5)
    likelihood: int = Field(ge=1, le=5)


@router.get("")
def list_risks(request: Request):
    with get_conn() as conn:
        rows = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM risks ORDER BY residual_risk DESC"
            ).fetchall()
        ]
    return ok(rows, request.state.request_id)


@router.post("")
def create_risk(body: RiskIn, request: Request):
    residual = body.severity * body.likelihood
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO risks(hazard,site,department,controls,severity,likelihood,residual_risk,status,created_at) VALUES(?,?,?,?,?,?,?,?,datetime('now'))",
            (
                body.hazard,
                body.site,
                body.department,
                body.controls,
                body.severity,
                body.likelihood,
                residual,
                "open",
            ),
        )
        conn.commit()
    return ok(
        {"id": cur.lastrowid, "residual_risk": residual}, request.state.request_id
    )


@router.get("/matrix")
def matrix(request: Request):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT severity, likelihood, COUNT(*) c FROM risks GROUP BY severity, likelihood"
        ).fetchall()
    return ok([dict(r) for r in rows], request.state.request_id)


@router.get("/top")
def top_risks(request: Request):
    with get_conn() as conn:
        rows = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM risks ORDER BY residual_risk DESC LIMIT 5"
            ).fetchall()
        ]
    return ok(rows, request.state.request_id)
