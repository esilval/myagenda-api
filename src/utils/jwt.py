from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt


def _get_secret() -> str:
    secret = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY")
    if not secret:
        # dev fallback only
        secret = "dev-secret"
    return secret


def create_access_token(payload: Dict[str, Any], expires_minutes: int = 30) -> str:
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    to_encode.update({"iat": int(now.timestamp()), "exp": int((now + timedelta(minutes=expires_minutes)).timestamp())})
    token = jwt.encode(to_encode, _get_secret(), algorithm="HS256")
    return token


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, _get_secret(), algorithms=["HS256"])


