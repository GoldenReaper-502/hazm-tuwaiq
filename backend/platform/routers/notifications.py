from fastapi import APIRouter, Request

from backend.platform.db import get_conn
from backend.platform.responses import ok

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def list_notifications(request: Request):
    with get_conn() as conn:
        rows = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM notifications ORDER BY id DESC LIMIT 200"
            ).fetchall()
        ]
    return ok(rows, request.state.request_id)


@router.get("/unread-count")
def unread_count(request: Request):
    with get_conn() as conn:
        c = conn.execute(
            "SELECT COUNT(*) c FROM notifications WHERE status='unread'"
        ).fetchone()["c"]
    return ok({"unread": c}, request.state.request_id)


@router.post("/mark-read")
def mark_read(request: Request, payload: dict):
    ids = payload.get("ids", [])
    if not ids:
        return ok({"updated": 0}, request.state.request_id)
    placeholders = ",".join(["?" for _ in ids])
    with get_conn() as conn:
        cur = conn.execute(
            f"UPDATE notifications SET status='read' WHERE id IN ({placeholders})", ids
        )
        conn.commit()
    return ok({"updated": cur.rowcount}, request.state.request_id)
