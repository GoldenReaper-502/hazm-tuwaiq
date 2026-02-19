from fastapi import APIRouter, Request

from backend.platform.responses import ok

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.post("/webhook/test")
def webhook_test(request: Request):
    return ok({"sent": True, "target": "webhook_stub"}, request.state.trace_id)
