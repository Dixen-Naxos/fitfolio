from httpx import AsyncClient

from tests.conftest import auth_headers, register_user


async def test_logout_all_invalidates_existing_access_token(client: AsyncClient) -> None:
    data = await register_user(client, "logout-access@example.com")
    access_token = data["access_token"]

    # Token works before logout-all.
    before = await client.get("/api/v1/users/me", headers=auth_headers(access_token))
    assert before.status_code == 200

    logout = await client.post("/api/v1/auth/logout-all", headers=auth_headers(access_token))
    assert logout.status_code == 204

    # The same access token is now rejected.
    after = await client.get("/api/v1/users/me", headers=auth_headers(access_token))
    assert after.status_code == 401


async def test_logout_all_invalidates_existing_refresh_token(client: AsyncClient) -> None:
    data = await register_user(client, "logout-refresh@example.com")
    access_token = data["access_token"]
    refresh_token = data["refresh_token"]

    logout = await client.post("/api/v1/auth/logout-all", headers=auth_headers(access_token))
    assert logout.status_code == 204

    # The old refresh token can no longer mint new tokens.
    refresh = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh.status_code == 401


async def test_login_after_logout_all_yields_usable_tokens(client: AsyncClient) -> None:
    data = await register_user(client, "logout-relogin@example.com")
    await client.post("/api/v1/auth/logout-all", headers=auth_headers(data["access_token"]))

    # Logging in again issues tokens carrying the bumped version, so they work.
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "logout-relogin@example.com", "password": "Str0ngPass!23"},
    )
    assert login.status_code == 200
    new_access = login.json()["access_token"]

    me = await client.get("/api/v1/users/me", headers=auth_headers(new_access))
    assert me.status_code == 200


async def test_logout_all_requires_authentication(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/logout-all")
    assert response.status_code in (401, 403)
