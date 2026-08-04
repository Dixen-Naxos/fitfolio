import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

import bcrypt
import jwt

from app.core.config import settings

TokenType = Literal["access", "refresh"]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def _create_token(subject: str, token_type: TokenType, expires_delta: timedelta) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "jti": jti,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, jti


def create_access_token(subject: str) -> str:
    token, _ = _create_token(
        subject, "access", timedelta(minutes=settings.access_token_expire_minutes)
    )
    return token


def create_refresh_token(subject: str) -> tuple[str, str]:
    """Returns (token, jti). The jti is persisted so the refresh token can be revoked on logout."""
    return _create_token(subject, "refresh", timedelta(days=settings.refresh_token_expire_days))


class InvalidTokenError(Exception):
    pass


def decode_token(token: str, expected_type: TokenType) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise InvalidTokenError(str(exc)) from exc

    if payload.get("type") != expected_type:
        raise InvalidTokenError(f"Expected a {expected_type} token")

    return payload
