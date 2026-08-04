import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class FriendshipStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"
    blocked = "blocked"


class Friendship(Base):
    __tablename__ = "friendships"
    __table_args__ = (
        UniqueConstraint("requester_id", "addressee_id", name="uq_friendship_pair"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    requester_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    addressee_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[FriendshipStatus] = mapped_column(
        Enum(FriendshipStatus, name="friendship_status"),
        default=FriendshipStatus.pending,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    requester: Mapped["User"] = relationship(foreign_keys=[requester_id])
    addressee: Mapped["User"] = relationship(foreign_keys=[addressee_id])
