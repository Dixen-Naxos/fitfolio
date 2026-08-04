import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.clothing_item import ClothingItem
    from app.models.outfit import Outfit


class OutfitItem(Base):
    __tablename__ = "outfit_items"

    outfit_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("outfits.id", ondelete="CASCADE"), primary_key=True
    )
    clothing_item_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("clothing_items.id", ondelete="CASCADE"), primary_key=True
    )

    outfit: Mapped["Outfit"] = relationship(back_populates="item_links")
    clothing_item: Mapped["ClothingItem"] = relationship(back_populates="outfit_links")
