from pydantic import BaseModel, EmailStr, Field, model_validator

from app.core.passwords import validate_password_strength
from app.schemas.user import UserRead


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(max_length=128)
    display_name: str = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def _enforce_password_policy(self) -> "RegisterRequest":
        validate_password_strength(
            self.password, email=self.email, display_name=self.display_name
        )
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(TokenPair):
    user: UserRead
