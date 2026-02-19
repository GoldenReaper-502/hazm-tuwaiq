from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from backend.platform.db import get_conn
from backend.platform.responses import fail, ok

router = APIRouter(prefix="/cameras", tags=["cameras"])


class CameraIn(BaseModel):
    name: str
    site: str
    location: str
    stream_url: str = ""


class CameraPatch(BaseModel):
    name: str | None = None
    site: str | None = None
    location: str | None = None
    status: str | None = None
    stream_url: str | None = None


@router.get("")
def list_cameras(request: Request):
    with get_conn() as conn:
        rows = [
            dict(r)
            for r in conn.execute("SELECT * FROM cameras ORDER BY id DESC").fetchall()
        ]
    return ok(rows, request.state.request_id)


@router.post("")
def create_camera(body: CameraIn, request: Request):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO cameras(name,site,location,status,stream_url,last_health_check) VALUES(?,?,?,?,?,?)",
            (
                body.name,
                body.site,
                body.location,
                "online",
                body.stream_url,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
    return ok({"id": cur.lastrowid}, request.state.request_id)


@router.get("/{camera_id}")
def get_camera(camera_id: int, request: Request):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM cameras WHERE id=?", (camera_id,)).fetchone()
    if not row:
        raise HTTPException(
            status_code=404,
            detail=fail(
                "CAMERA_NOT_FOUND", "Camera not found", request.state.request_id
            ),
        )
    return ok(dict(row), request.state.request_id)


@router.patch("/{camera_id}")
def patch_camera(camera_id: int, body: CameraPatch, request: Request):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        return ok({"updated": False}, request.state.request_id)
    sets = ", ".join([f"{k}=?" for k in updates])
    params = list(updates.values()) + [camera_id]
    with get_conn() as conn:
        cur = conn.execute(f"UPDATE cameras SET {sets} WHERE id=?", params)
        conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=fail(
                "CAMERA_NOT_FOUND", "Camera not found", request.state.request_id
            ),
        )
    return ok({"updated": True}, request.state.request_id)


@router.get("/{camera_id}/health")
def camera_health(camera_id: int, request: Request):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id,status,last_health_check FROM cameras WHERE id=?", (camera_id,)
        ).fetchone()
    if not row:
        raise HTTPException(
            status_code=404,
            detail=fail(
                "CAMERA_NOT_FOUND", "Camera not found", request.state.request_id
            ),
        )
    return ok(
        {
            "camera_id": camera_id,
            "status": row["status"],
            "last_health_check": row["last_health_check"],
        },
        request.state.request_id,
    )


@router.get("/groups")
def camera_groups(request: Request):
    with get_conn() as conn:
        rows = [
            dict(r)
            for r in conn.execute(
                "SELECT site, COUNT(*) count FROM cameras GROUP BY site"
            ).fetchall()
        ]
    return ok(rows, request.state.request_id)
