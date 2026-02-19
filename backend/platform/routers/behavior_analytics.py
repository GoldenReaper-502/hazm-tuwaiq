from fastapi import APIRouter, Request
from pydantic import BaseModel
from backend.platform.responses import ok

router = APIRouter(prefix="/behavior-analytics", tags=["behavior_analytics"])


class BehaviorInput(BaseModel):
    team: str
    at_risk_frequency: int
    compliance_score: float
    shift_length_hours: float
    overtime_hours: float


@router.post("/score")
def score(body: BehaviorInput, request: Request):
    fatigue_risk = min(100.0, body.shift_length_hours * 5 + body.overtime_hours * 8)
    behavior_score = max(0.0, 100 - body.at_risk_frequency * 2 - (100 - body.compliance_score) - fatigue_risk * 0.2)
    interventions = []
    if body.at_risk_frequency > 15:
        interventions.append("toolbox_talk")
    if fatigue_risk > 60:
        interventions.append("supervisor_coaching")
    if body.compliance_score < 70:
        interventions.append("signage")
    if not interventions:
        interventions.append("engineering_control")
    return ok({"team": body.team, "behavior_score": round(behavior_score, 2), "fatigue_risk": round(fatigue_risk, 2), "recommendations": interventions}, request.state.trace_id)


@router.get("/top-risks")
def top_risks(request: Request):
    return ok({"top_risk_behaviors": ["PPE non-compliance", "unsafe lifting", "mobile distraction"], "top_interventions": ["toolbox talk", "supervisor coaching", "engineering control"]}, request.state.trace_id)
