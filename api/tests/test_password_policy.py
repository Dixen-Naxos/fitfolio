import pytest
from httpx import AsyncClient

from app.core.passwords import PasswordPolicyError, validate_password_strength


@pytest.mark.parametrize(
    "password",
    [
        "Short1!",            # too short (< 10)
        "password123",        # common/breached
        "aaaaaaaaaa",         # single repeated char
        "abcdefghij",         # only one character class
        "1234567890",         # only one character class (digits)
    ],
)
def test_validate_rejects_weak_passwords(password: str) -> None:
    with pytest.raises(PasswordPolicyError):
        validate_password_strength(password)


def test_validate_rejects_password_containing_email_local_part() -> None:
    with pytest.raises(PasswordPolicyError):
        validate_password_strength("Alice-Wonderland7", email="alice@example.com")


def test_validate_rejects_password_containing_display_name() -> None:
    with pytest.raises(PasswordPolicyError):
        validate_password_strength("Bobby-Tables99", display_name="bobby")


def test_validate_accepts_strong_password() -> None:
    assert validate_password_strength(
        "Str0ngPass!23", email="user@example.com", display_name="User"
    ) == "Str0ngPass!23"


async def test_register_rejects_weak_password(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "weakpw@example.com", "password": "password123", "display_name": "Weak"},
    )
    assert response.status_code == 422


async def test_register_accepts_strong_password(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "strongpw@example.com", "password": "Str0ngPass!23", "display_name": "Strong"},
    )
    assert response.status_code == 201
