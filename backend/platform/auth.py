from datetime import datetime, timedelta, timezone
from typing import Any
import uuid
import bcrypt
import jwt
from fastapi import HTTPException, Header
from backend.platform.config import settings
from backend.platform.db import get_conn

ROLE_MAP = {
    "Admin": "admin",
    "HSE Officer": "hse",
    "Supervisor": "supervisor",
    "Viewer": "viewer",
    "Auditor": "auditor",
    "admin": "admin",
    "hse": "hse",
    "supervisor": "supervisor",
    "viewer": "viewer",
    "auditor": "auditor",
}

BLACKLIST: set[str] = set()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(username: str, role: str, token_type: str = "access", minutes: int | None = None) -> str:
    expiry_mins = minutes if minutes is not None else settings.access_token_expire_minutes
    exp = datetime.now(timezone.utc) + timedelta(minutes=expiry_mins)
    payload: dict[str, Any] = {
        "sub": username,
        "role": ROLE_MAP.get(role, role).lower(),
        "type": token_type,
        "exp": exp,
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_token(token: str) -> dict:
    if token in BLACKLIST:
        raise HTTPException(status_code=401, detail="Token revoked")
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


def current_user(authorization: str = Header(default="")) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    with get_conn() as conn:
        row = conn.execute("SELECT username, role, department, full_name, site FROM users WHERE username=?", (payload["sub"],)).fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="User not found")
    data = dict(row)
    data["role"] = ROLE_MAP.get(data["role"], data["role"]).lower()
    return data


def require_role(role: str):
    role = role.lower()

    async def dep(authorization: str = Header(default="")):
        user_data = current_user(authorization)
        if user_data["role"] != role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user_data

    return dep


def require_any_role(roles: list[str]):
    roles = [r.lower() for r in roles]

    async def dep(authorization: str = Header(default="")):
        user_data = current_user(authorization)
        if user_data["role"] not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user_data

    return dep
