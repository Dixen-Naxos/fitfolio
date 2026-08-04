import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RevokedToken(Base):
    """Tracks revoked refresh-token jtis so /auth/logout can actually invalidate a session."""

    __tablename__ = "revoked_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    jti: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
