import time
import uuid
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.platform.config import settings
from backend.platform.responses import fail

METRICS = {"requests_total": 0, "requests_by_path": defaultdict(int)}
_BUCKETS = defaultdict(deque)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        request.state.trace_id = request_id
        start = time.time()
        METRICS["requests_total"] += 1
        METRICS["requests_by_path"][request.url.path] += 1
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{(time.time() - start) * 1000:.2f}"
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        key = f"{ip}:{request.url.path}"
        now = time.time()
        window = 60
        q = _BUCKETS[key]
        while q and now - q[0] > window:
            q.popleft()
        if len(q) >= settings.rate_limit_per_minute:
            return JSONResponse(
                status_code=429,
                content=fail(
                    "RATE_LIMIT",
                    "Rate limit exceeded",
                    getattr(request.state, "request_id", "n/a"),
                ),
            )
        q.append(now)
        return await call_next(request)
