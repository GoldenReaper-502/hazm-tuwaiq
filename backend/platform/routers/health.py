from fastapi import APIRouter, Request
from backend.platform.middleware import METRICS
from backend.platform.responses import ok

router = APIRouter(tags=["health"])

@router.get("/health")
def health(request: Request):
    return ok({"status": "healthy"}, request.state.request_id)

@router.get("/metrics")
def metrics(request: Request):
    return ok({"requests_total": METRICS["requests_total"], "requests_by_path": dict(METRICS["requests_by_path"])}, request.state.request_id)
