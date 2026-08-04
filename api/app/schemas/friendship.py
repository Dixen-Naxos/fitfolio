import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.friendship import FriendshipStatus
from app.schemas.user import UserRead


class FriendRequestCreate(BaseModel):
    addressee_email: EmailStr


class FriendshipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    requester_id: uuid.UUID
    addressee_id: uuid.UUID
    status: FriendshipStatus
    created_at: datetime


class FriendRead(BaseModel):
    friendship_id: uuid.UUID
    user: UserRead
