from datetime import datetime, timezone
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Hazm Tuwaiq API", version="0.1.0")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------- Models ----------
class HealthResponse(BaseModel):
    status: str
    service: str
    time_utc: str


class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=120)
    location: Optional[str] = None
    description: Optional[str] = None
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")


class Incident(IncidentCreate):
    id: int
    created_at_utc: str


# ---------- In-memory DB (MVP) ----------
INCIDENTS: List[Incident] = []
NEXT_ID = 1


# ---------- Routes ----------
@app.get("/", response_model=HealthResponse)
def root():
    return {
        "status": "ok",
        "service": "Hazm Tuwaiq backend is running",
        "time_utc": utc_now(),
    }


@app.get("/incidents", response_model=List[Incident])
def list_incidents():
    return INCIDENTS


@app.post("/incidents", response_model=Incident)
def create_incident(data: IncidentCreate):
    global NEXT_ID
    item = Incident(
        id=NEXT_ID,
        created_at_utc=utc_now(),
        **data.model_dump(),
    )
    INCIDENTS.append(item)
    NEXT_ID += 1
    return item


@app.get("/incidents/{incident_id}", response_model=Incident)
def get_incident(incident_id: int):
    for item in INCIDENTS:
        if item.id == incident_id:
            return item
    raise HTTPException(status_code=404, detail="Incident not found")

