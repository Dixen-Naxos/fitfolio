from httpx import AsyncClient

from tests.conftest import auth_headers, register_user


async def test_friend_request_flow(client: AsyncClient) -> None:
    alice = await register_user(client, "alice-friend@example.com")
    bob = await register_user(client, "bob-friend@example.com")

    request_response = await client.post(
        "/api/v1/friends/requests",
        json={"addressee_email": "bob-friend@example.com"},
        headers=auth_headers(alice["access_token"]),
    )
    assert request_response.status_code == 201
    friendship_id = request_response.json()["id"]
    assert request_response.json()["status"] == "pending"

    incoming_response = await client.get(
        "/api/v1/friends/requests?direction=incoming", headers=auth_headers(bob["access_token"])
    )
    assert incoming_response.status_code == 200
    assert len(incoming_response.json()) == 1

    accept_response = await client.post(
        f"/api/v1/friends/requests/{friendship_id}/accept", headers=auth_headers(bob["access_token"])
    )
    assert accept_response.status_code == 200
    assert accept_response.json()["status"] == "accepted"

    alice_friends = await client.get("/api/v1/friends", headers=auth_headers(alice["access_token"]))
    assert alice_friends.status_code == 200
    assert alice_friends.json()[0]["user"]["email"] == "bob-friend@example.com"

    bob_friends = await client.get("/api/v1/friends", headers=auth_headers(bob["access_token"]))
    assert bob_friends.json()[0]["user"]["email"] == "alice-friend@example.com"


async def test_cannot_friend_request_self(client: AsyncClient) -> None:
    alice = await register_user(client, "alice-self@example.com")
    response = await client.post(
        "/api/v1/friends/requests",
        json={"addressee_email": "alice-self@example.com"},
        headers=auth_headers(alice["access_token"]),
    )
    assert response.status_code == 400


async def test_duplicate_friend_request_rejected(client: AsyncClient) -> None:
    alice = await register_user(client, "alice-dup@example.com")
    await register_user(client, "bob-dup@example.com")

    headers = auth_headers(alice["access_token"])
    first = await client.post(
        "/api/v1/friends/requests", json={"addressee_email": "bob-dup@example.com"}, headers=headers
    )
    assert first.status_code == 201

    second = await client.post(
        "/api/v1/friends/requests", json={"addressee_email": "bob-dup@example.com"}, headers=headers
    )
    assert second.status_code == 409
