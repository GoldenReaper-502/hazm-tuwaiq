from fastapi import APIRouter, Request

from backend.platform.middleware import METRICS

router = APIRouter(tags=["health"])


@router.get("/health")
def health(request: Request):
    return {"status": "ok"}


@router.get("/metrics")
def metrics(request: Request):
    return {
        "requests_total": METRICS["requests_total"],
        "requests_by_path": dict(METRICS["requests_by_path"]),
    }
