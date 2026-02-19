from datetime import datetime, timezone
from fastapi import APIRouter, Request
from backend.platform.responses import ok
from backend.platform.db import get_conn

router = APIRouter(prefix="/ops", tags=["ops"])


@router.post("/heartbeat")
def heartbeat(request: Request, payload: dict):
    camera_id = int(payload.get("camera_id", 0))
    status = payload.get("status", "online")
    with get_conn() as conn:
        conn.execute("UPDATE cameras SET status=?, last_health_check=? WHERE id=?", (status, datetime.now(timezone.utc).isoformat(), camera_id))
        conn.commit()
    return ok({"camera_id": camera_id, "status": status}, request.state.request_id)
