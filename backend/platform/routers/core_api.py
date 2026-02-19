from datetime import datetime, timezone

from fastapi import APIRouter, Request

from backend.platform.middleware import METRICS
from backend.platform.responses import ok

router = APIRouter(prefix="/core", tags=["core_api"])


@router.get("/health")
def health(request: Request):
    return ok({"status": "healthy", "service": "hse-platform"}, request.state.trace_id)


@router.get("/status")
def status(request: Request):
    return ok(
        {"version": "1.0.0", "time": datetime.now(timezone.utc).isoformat()},
        request.state.trace_id,
    )


@router.get("/metrics")
def metrics(request: Request):
    return ok(
        {
            "requests_total": METRICS["requests_total"],
            "requests_by_path": dict(METRICS["requests_by_path"]),
        },
        request.state.trace_id,
    )

    return health(request)

    return metrics(request)
