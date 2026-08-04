import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.share import ResourceType
from app.schemas.clothing_item import ClothingItemRead
from app.schemas.outfit import OutfitRead


class ShareCreate(BaseModel):
    shared_with_email: EmailStr


class ShareRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resource_type: ResourceType
    resource_id: uuid.UUID
    owner_id: uuid.UUID
    shared_with_id: uuid.UUID
    created_at: datetime


class SharedClothingItem(BaseModel):
    share: ShareRead
    clothing_item: ClothingItemRead


class SharedOutfit(BaseModel):
    share: ShareRead
    outfit: OutfitRead


class SharedWithMeResponse(BaseModel):
    clothing_items: list[SharedClothingItem]
    outfits: list[SharedOutfit]
