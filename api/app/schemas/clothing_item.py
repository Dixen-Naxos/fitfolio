import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.clothing_item import ClothingCategory


class ClothingItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    category: ClothingCategory
    color: str | None = Field(default=None, max_length=50)
    tags: list[str] = Field(default_factory=list)


class ClothingItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    category: ClothingCategory | None = None
    color: str | None = Field(default=None, max_length=50)
    tags: list[str] | None = None


class ClothingItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    category: ClothingCategory
    color: str | None
    tags: list[str]
    image_url: str | None = None
    created_at: datetime


class UploadUrlRequest(BaseModel):
    content_type: str = Field(default="image/jpeg", max_length=100)


class UploadUrlResponse(BaseModel):
    upload_url: str
    object_key: str


class ConfirmImageRequest(BaseModel):
    object_key: str
