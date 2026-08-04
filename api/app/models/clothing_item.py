import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.outfit_item import OutfitItem
    from app.models.user import User


class ClothingCategory(str, enum.Enum):
    top = "top"
    bottom = "bottom"
    outerwear = "outerwear"
    shoes = "shoes"
    accessory = "accessory"
    dress = "dress"
    other = "other"


class ClothingItem(Base):
    __tablename__ = "clothing_items"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[ClothingCategory] = mapped_column(
        Enum(ClothingCategory, name="clothing_category"), nullable=False
    )
    color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    image_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User"] = relationship(back_populates="clothing_items")
    outfit_links: Mapped[list["OutfitItem"]] = relationship(
        back_populates="clothing_item", cascade="all, delete-orphan"
    )
