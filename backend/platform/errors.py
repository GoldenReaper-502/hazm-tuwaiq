from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.platform.responses import fail


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", "n/a")
    return JSONResponse(
        status_code=422,
        content=fail("VALIDATION_ERROR", "Invalid input", request_id, exc.errors()),
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", "n/a")
    if isinstance(exc.detail, dict) and "ok" in exc.detail:
        content = exc.detail
    else:
        content = fail("HTTP_ERROR", str(exc.detail), request_id)
    return JSONResponse(status_code=exc.status_code, content=content)


async def generic_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "n/a")
    return JSONResponse(
        status_code=500, content=fail("INTERNAL_ERROR", str(exc), request_id)
    )
