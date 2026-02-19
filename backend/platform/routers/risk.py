from fastapi import APIRouter, Request
from pydantic import BaseModel
from backend.platform.responses import ok

router = APIRouter(prefix="/risk", tags=["risk_assessment"])


class Hazard(BaseModel):
    hazard: str
    controls: str
    severity: int
    likelihood: int


class JSAIn(BaseModel):
    task_name: str
    hazards: list[Hazard]


@router.post("/jsa")
def create_jsa(body: JSAIn, request: Request):
    residual = []
    for h in body.hazards:
        score = h.severity * h.likelihood
        residual.append({"hazard": h.hazard, "controls": h.controls, "residual_risk": max(1, score - 3)})
    return ok({"task": body.task_name, "template": "JSA/JHA", "residual": residual, "pdf_export": "/api/v1/reports/export/pdf"}, request.state.trace_id)
