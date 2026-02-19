import json
from datetime import datetime, timezone
from fastapi import APIRouter, Request
from pydantic import BaseModel
from backend.platform.responses import ok
from backend.platform.db import get_conn

router = APIRouter(prefix="/environment", tags=["environment"])
DEFAULT_THRESHOLDS = {"noise": 85, "dust": 150, "VOC": 300, "temp": 45, "humidity": 70, "CO2": 1000}


class EnvIn(BaseModel):
    metric: str
    value: float
    unit: str
    location: str
    site: str = "HQ"
    measured_at: str | None = None


@router.get("/readings")
def list_readings(request: Request, site: str | None = None):
    q = "SELECT * FROM environment_measurements"
    params = []
    if site:
        q += " WHERE site=?"
        params.append(site)
    q += " ORDER BY id DESC LIMIT 200"
    with get_conn() as conn:
        rows = [dict(r) for r in conn.execute(q, tuple(params)).fetchall()]
    return ok(rows, request.state.request_id)


@router.post("/readings")
def add_reading(body: EnvIn, request: Request):
    measured_at = body.measured_at or datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        site_row = conn.execute("SELECT threshold_json FROM sites WHERE name=?", (body.site,)).fetchone()
        thresholds = json.loads(site_row["threshold_json"]) if site_row and site_row["threshold_json"] else DEFAULT_THRESHOLDS
        limit = thresholds.get(body.metric, DEFAULT_THRESHOLDS.get(body.metric, 999999))
        exceeded = int(body.value > limit)
        cur = conn.execute("INSERT INTO environment_measurements(metric,value,unit,location,site,measured_at,exceeded) VALUES(?,?,?,?,?,?,?)", (body.metric, body.value, body.unit, body.location, body.site, measured_at, exceeded))
        if exceeded:
            conn.execute("INSERT INTO alert_events(rule_name,severity,payload_json,channel,created_at) VALUES(?,?,?,?,?)", ("environment_threshold", "high", json.dumps({"metric": body.metric, "value": body.value, "limit": limit, "site": body.site}), "in_app", measured_at))
        conn.commit()
    return ok({"id": cur.lastrowid, "threshold": limit, "threshold_exceeded": bool(exceeded)}, request.state.request_id)


@router.get("/alerts")
def env_alerts(request: Request):
    with get_conn() as conn:
        rows = [dict(r) for r in conn.execute("SELECT * FROM alert_events WHERE rule_name='environment_threshold' ORDER BY id DESC LIMIT 100").fetchall()]
    return ok(rows, request.state.request_id)


@router.get("/summary")
def env_summary(request: Request, site: str = "HQ"):
    with get_conn() as conn:
        rows = conn.execute("SELECT metric, AVG(value) avg_value, MAX(value) max_value, SUM(exceeded) exceedances FROM environment_measurements WHERE site=? GROUP BY metric", (site,)).fetchall()
    return ok({"site": site, "metrics": [dict(r) for r in rows]}, request.state.request_id)


@router.get("/thresholds")
def thresholds(request: Request, site: str = "HQ"):
    with get_conn() as conn:
        row = conn.execute("SELECT threshold_json FROM sites WHERE name=?", (site,)).fetchone()
    data = json.loads(row["threshold_json"]) if row and row["threshold_json"] else DEFAULT_THRESHOLDS
    return ok({"site": site, "thresholds": data}, request.state.request_id)
