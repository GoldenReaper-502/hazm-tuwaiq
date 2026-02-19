from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel


class APIError(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class APIMeta(BaseModel):
    request_id: str
    timestamp: str
    trace: dict[str, Any] | None = None


class APIResponse(BaseModel):
    ok: bool
    data: Optional[Any] = None
    error: Optional[APIError] = None
    meta: APIMeta
    # backward compatibility fields
    success: Optional[bool] = None
    trace_id: Optional[str] = None
    timestamp: Optional[str] = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ok(data: Any, request_id: str) -> dict:
    now = _now()
    return APIResponse(
        ok=True,
        data=data,
        error=None,
        meta=APIMeta(request_id=request_id, timestamp=now, trace={"version": "v1"}),
        success=True,
        trace_id=request_id,
        timestamp=now,
    ).model_dump()


def fail(code: str, message: str, request_id: str, details: Any = None) -> dict:
    now = _now()
    return APIResponse(
        ok=False,
        data=None,
        error=APIError(code=code, message=message, details=details),
        meta=APIMeta(request_id=request_id, timestamp=now, trace={"version": "v1"}),
        success=False,
        trace_id=request_id,
        timestamp=now,
    ).model_dump()
