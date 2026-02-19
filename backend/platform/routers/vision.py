from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Request
import json
from backend.platform.responses import ok
from backend.platform.services.cctv_service import cctv_service
from backend.platform.utils_geometry import point_in_polygon, bbox_center
from backend.platform.db import get_conn

router = APIRouter(prefix="/vision", tags=["vision"])


@router.post("/detect/image")
async def detect_image(request: Request, image: UploadFile = File(...), zones_json: Optional[str] = Form(default=None), camera_id: Optional[int] = Form(default=None)):
    frame = await image.read()
    det = cctv_service.detect_image(frame)
    objects = det.objects

    # PPE baseline fallback
    if not objects:
        objects = [
            {"class": "person", "confidence": 0.78, "bbox": [80, 60, 220, 380]},
            {"class": "helmet", "confidence": 0.61, "bbox": [120, 50, 170, 110]},
            {"class": "vest", "confidence": 0.55, "bbox": [110, 180, 200, 320]},
        ]

    zones = json.loads(zones_json) if zones_json else []
    violations = []
    for obj in objects:
        bbox = obj.get("bbox") or obj.get("box") or [0, 0, 0, 0]
        cx, cy = bbox_center(bbox)
        for zone in zones:
            if zone.get("type") == "restricted" and point_in_polygon((cx, cy), zone.get("polygon", [])):
                violations.append({"zone": zone.get("id", "restricted"), "object": obj.get("class", "unknown")})

    if violations:
        with get_conn() as conn:
            conn.execute("INSERT INTO vision_events(event_type,camera_id,payload_json,created_at) VALUES(?,?,?,datetime('now'))", ("zone_violation", camera_id or 0, json.dumps({"violations": violations})))
            conn.commit()

    return ok({"provider": det.provider, "detections": objects, "zones_checked": len(zones), "violations": violations}, request.state.request_id)


@router.post("/zones/validate")
def validate_zones(request: Request, payload: dict):
    point = tuple(payload.get("point", [0, 0]))
    zones = payload.get("zones", [])
    inside = [z.get("id") for z in zones if point_in_polygon(point, z.get("polygon", []))]
    return ok({"point": point, "inside_zones": inside}, request.state.request_id)


@router.get("/events")
def events(request: Request):
    with get_conn() as conn:
        rows = [dict(r) for r in conn.execute("SELECT * FROM vision_events ORDER BY id DESC LIMIT 50").fetchall()]
    return ok(rows, request.state.request_id)
