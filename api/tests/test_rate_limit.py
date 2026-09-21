from httpx import AsyncClient

from app.core.config import settings
from app.core.rate_limit import limiter
from tests.conftest import register_user


async def test_login_is_rate_limited(client: AsyncClient, monkeypatch) -> None:
    # Opt back into rate limiting (the suite disables it by default) with a low, deterministic
    # login limit. The endpoint reads the limit from settings at request time, so this takes effect.
    monkeypatch.setattr(settings, "auth_login_rate_limit", "3/minute")
    limiter.enabled = True
    limiter.reset()

    await register_user(client, "rl@example.com")

    # The first 3 attempts are allowed (wrong password -> 401); the 4th is blocked -> 429.
    for _ in range(3):
        response = await client.post(
            "/api/v1/auth/login", json={"email": "rl@example.com", "password": "wrong-password"}
        )
        assert response.status_code == 401, response.text

    blocked = await client.post(
        "/api/v1/auth/login", json={"email": "rl@example.com", "password": "wrong-password"}
    )
    assert blocked.status_code == 429, blocked.text


async def test_rate_limit_disabled_allows_many_attempts(client: AsyncClient) -> None:
    # With the limiter disabled (suite default), repeated wrong logins never hit 429.
    await register_user(client, "norl@example.com")
    for _ in range(15):
        response = await client.post(
            "/api/v1/auth/login", json={"email": "norl@example.com", "password": "wrong-password"}
        )
        assert response.status_code == 401, response.text
