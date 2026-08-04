import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class ResourceType(str, enum.Enum):
    clothing_item = "clothing_item"
    outfit = "outfit"


class Share(Base):
    __tablename__ = "shares"
    __table_args__ = (
        UniqueConstraint(
            "resource_type", "resource_id", "shared_with_id", name="uq_share_resource_user"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    resource_type: Mapped[ResourceType] = mapped_column(
        Enum(ResourceType, name="share_resource_type"), nullable=False
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    shared_with_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User"] = relationship(foreign_keys=[owner_id])
    shared_with: Mapped["User"] = relationship(foreign_keys=[shared_with_id])
