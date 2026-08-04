import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.clothing_item import ClothingItemRead


class OutfitCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)


class OutfitUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)


class SetOutfitItemsRequest(BaseModel):
    clothing_item_ids: list[uuid.UUID]


class OutfitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    created_at: datetime
    items: list[ClothingItemRead] = Field(default_factory=list)
