from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Hazm Tuwaiq API", version="0.1.0")


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


INCIDENTS: List[Incident] = []
incident_id = 1


def utc_now():
    return datetime.utcnow().isoformat() + "Z"


@app.get("/", response_model=HealthResponse)
def root():
    return {
        "status": "ok",
        "service": "Hazm Tuwaiq backend is running",
        "time_utc": utc_now(),
    }


@app.post("/incidents", response_model=Incident)
def create_incident(data: IncidentCreate):
    global incident_id
    item = Incident(
        id=incident_id,
        created_at_utc=utc_now(),
        **data.model_dump(),
    )
    INCIDENTS.append(item)
    incident_id += 1
    return item


@app.get("/incidents", response_model=List[Incident])
def list_incidents():
    return INCIDENTS
