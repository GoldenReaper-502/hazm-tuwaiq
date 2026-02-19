import time
from collections import defaultdict, deque

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel

from backend.platform.auth import (
    BLACKLIST,
    create_token,
    current_user,
    decode_token,
    verify_password,
)
from backend.platform.bootstrap import seed_demo_data
from backend.platform.db import get_conn
from backend.platform.responses import fail, ok
from backend.platform.services.audit_service import audit_event

router = APIRouter(prefix="/auth", tags=["auth"])
_LOGIN_BUCKETS = defaultdict(deque)


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/login")
def login(body: LoginRequest, request: Request):
    seed_demo_data()
    ip = request.client.host if request.client else "unknown"
    key = f"{ip}:{body.username}"
    q = _LOGIN_BUCKETS[key]
    now = time.time()
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= 10:
        raise HTTPException(
            status_code=429,
            detail=fail(
                "LOGIN_RATE_LIMIT", "Too many login attempts", request.state.request_id
            ),
        )
    q.append(now)

    with get_conn() as conn:
        row = conn.execute(
            "SELECT username, password_hash, role, full_name FROM users WHERE username=?",
            (body.username,),
        ).fetchone()
    if not row or not verify_password(body.password, row["password_hash"]):
        audit_event(
            body.username,
            "login_failed",
            "auth",
            "0",
            {"reason": "invalid_credentials"},
        )
        raise HTTPException(
            status_code=401,
            detail=fail("AUTH_FAILED", "Invalid credentials", request.state.request_id),
        )
    access_token = create_token(row["username"], row["role"], token_type="access")
    refresh_token = create_token(
        row["username"], row["role"], token_type="refresh", minutes=60 * 24
    )
    audit_event(row["username"], "login", "auth", "0", {"role": row["role"]})
    return ok(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "username": row["username"],
                "role": row["role"],
                "full_name": row["full_name"],
            },
        },
        request.state.request_id,
    )


@router.post("/refresh")
def refresh(body: RefreshRequest, request: Request):
    payload = decode_token(body.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail=fail("AUTH_TYPE", "Invalid refresh token", request.state.request_id),
        )
    access_token = create_token(payload["sub"], payload["role"], token_type="access")
    audit_event(payload["sub"], "refresh", "auth", "0", {})
    return ok(
        {"access_token": access_token, "token_type": "bearer"}, request.state.request_id
    )


@router.post("/logout")
def logout(request: Request, authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail=fail("AUTH_MISSING", "Missing token", request.state.request_id),
        )
    token = authorization.replace("Bearer ", "")
    BLACKLIST.add(token)
    audit_event("system", "logout", "auth", "0", {})
    return ok({"logged_out": True}, request.state.request_id)


@router.get("/me")
def me(request: Request, authorization: str = Header(default="")):
    return ok(current_user(authorization), request.state.request_id)
