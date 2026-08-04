from httpx import AsyncClient

from tests.conftest import auth_headers, register_user


async def test_register_and_login(client: AsyncClient) -> None:
    data = await register_user(client, "alice@example.com")
    assert data["user"]["email"] == "alice@example.com"
    assert "access_token" in data
    assert "refresh_token" in data

    response = await client.post(
        "/api/v1/auth/login", json={"email": "alice@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_register_duplicate_email_rejected(client: AsyncClient) -> None:
    await register_user(client, "bob@example.com")
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "bob@example.com", "password": "password123", "display_name": "Bob 2"},
    )
    assert response.status_code == 409


async def test_login_wrong_password_rejected(client: AsyncClient) -> None:
    await register_user(client, "carol@example.com")
    response = await client.post(
        "/api/v1/auth/login", json={"email": "carol@example.com", "password": "wrong-password"}
    )
    assert response.status_code == 401


async def test_protected_route_requires_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/users/me")
    assert response.status_code in (401, 403)


async def test_protected_route_with_token(client: AsyncClient) -> None:
    data = await register_user(client, "dave@example.com")
    response = await client.get("/api/v1/users/me", headers=auth_headers(data["access_token"]))
    assert response.status_code == 200
    assert response.json()["email"] == "dave@example.com"


async def test_refresh_token_rotation_and_reuse_detection(client: AsyncClient) -> None:
    data = await register_user(client, "erin@example.com")
    refresh_token = data["refresh_token"]

    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    new_tokens = response.json()
    assert new_tokens["access_token"] != data["access_token"]

    # The old refresh token must not be reusable once rotated.
    reuse_response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert reuse_response.status_code == 401


async def test_logout_revokes_refresh_token(client: AsyncClient) -> None:
    data = await register_user(client, "frank@example.com")
    refresh_token = data["refresh_token"]

    logout_response = await client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert logout_response.status_code == 204

    refresh_response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 401
