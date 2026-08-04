import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.revoked_token import RevokedToken
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
)
from app.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


def _refresh_expiry(payload: dict) -> datetime:
    return datetime.fromtimestamp(payload["exp"], tz=timezone.utc)


async def _is_revoked(db: AsyncSession, jti: str) -> bool:
    result = await db.execute(select(RevokedToken).where(RevokedToken.jti == jti))
    return result.scalar_one_or_none() is not None


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(str(user.id))
    refresh_token, _ = create_refresh_token(str(user.id))
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.model_validate(user),
    )


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
    )
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise invalid_credentials

    access_token = create_access_token(str(user.id))
    refresh_token, _ = create_refresh_token(str(user.id))
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.model_validate(user),
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    invalid_token = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token"
    )
    try:
        token_payload = decode_token(payload.refresh_token, expected_type="refresh")
    except InvalidTokenError as exc:
        raise invalid_token from exc

    jti = token_payload.get("jti")
    if not jti or await _is_revoked(db, jti):
        raise invalid_token

    try:
        user_id = uuid.UUID(token_payload["sub"])
    except (KeyError, ValueError) as exc:
        raise invalid_token from exc

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise invalid_token

    # Rotate refresh token: revoke the one just used and issue a new pair.
    db.add(RevokedToken(jti=jti, expires_at=_refresh_expiry(token_payload)))
    new_access_token = create_access_token(str(user.id))
    new_refresh_token, _ = create_refresh_token(str(user.id))
    await db.commit()

    return TokenPair(access_token=new_access_token, refresh_token=new_refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: LogoutRequest, db: AsyncSession = Depends(get_db)) -> None:
    try:
        token_payload = decode_token(payload.refresh_token, expected_type="refresh")
    except InvalidTokenError:
        # Already invalid/expired: logout is idempotent, nothing to revoke.
        return None

    jti = token_payload.get("jti")
    if jti and not await _is_revoked(db, jti):
        db.add(RevokedToken(jti=jti, expires_at=_refresh_expiry(token_payload)))
        await db.commit()
    return None
