import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    display_name: str
    created_at: datetime


class UserUpdate(BaseModel):
    display_name: str | None = None
