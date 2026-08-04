from httpx import AsyncClient

from tests.conftest import auth_headers, register_user


async def _become_friends(client: AsyncClient, requester: dict, addressee_email: str) -> None:
    request_response = await client.post(
        "/api/v1/friends/requests",
        json={"addressee_email": addressee_email},
        headers=auth_headers(requester["access_token"]),
    )
    friendship_id = request_response.json()["id"]
    return friendship_id


async def test_share_requires_friendship(client: AsyncClient) -> None:
    owner = await register_user(client, "share-owner1@example.com")
    stranger = await register_user(client, "share-stranger1@example.com")

    item_response = await client.post(
        "/api/v1/clothes",
        json={"name": "Scarf", "category": "accessory"},
        headers=auth_headers(owner["access_token"]),
    )
    item_id = item_response.json()["id"]

    share_response = await client.post(
        f"/api/v1/clothes/{item_id}/share",
        json={"shared_with_email": "share-stranger1@example.com"},
        headers=auth_headers(owner["access_token"]),
    )
    assert share_response.status_code == 400

    # And the stranger still cannot see the item.
    get_response = await client.get(
        f"/api/v1/clothes/{item_id}", headers=auth_headers(stranger["access_token"])
    )
    assert get_response.status_code == 404


async def test_share_clothing_item_with_friend_and_unshare(client: AsyncClient) -> None:
    owner = await register_user(client, "share-owner2@example.com")
    friend = await register_user(client, "share-friend2@example.com")

    friendship_id = await _become_friends(client, owner, "share-friend2@example.com")
    accept_response = await client.post(
        f"/api/v1/friends/requests/{friendship_id}/accept", headers=auth_headers(friend["access_token"])
    )
    assert accept_response.status_code == 200

    item_response = await client.post(
        "/api/v1/clothes",
        json={"name": "Handbag", "category": "accessory"},
        headers=auth_headers(owner["access_token"]),
    )
    item_id = item_response.json()["id"]

    # Friend cannot see the item before it is shared.
    pre_share_response = await client.get(
        f"/api/v1/clothes/{item_id}", headers=auth_headers(friend["access_token"])
    )
    assert pre_share_response.status_code == 404

    share_response = await client.post(
        f"/api/v1/clothes/{item_id}/share",
        json={"shared_with_email": "share-friend2@example.com"},
        headers=auth_headers(owner["access_token"]),
    )
    assert share_response.status_code == 201

    post_share_response = await client.get(
        f"/api/v1/clothes/{item_id}", headers=auth_headers(friend["access_token"])
    )
    assert post_share_response.status_code == 200

    shared_with_me_response = await client.get(
        "/api/v1/shared-with-me", headers=auth_headers(friend["access_token"])
    )
    assert shared_with_me_response.status_code == 200
    assert len(shared_with_me_response.json()["clothing_items"]) == 1

    # Friend still cannot edit/delete the shared item (read-only sharing).
    patch_response = await client.patch(
        f"/api/v1/clothes/{item_id}", json={"name": "Hacked"}, headers=auth_headers(friend["access_token"])
    )
    assert patch_response.status_code == 404

    friend_id = friend["user"]["id"]
    unshare_response = await client.delete(
        f"/api/v1/clothes/{item_id}/share/{friend_id}", headers=auth_headers(owner["access_token"])
    )
    assert unshare_response.status_code == 204

    after_unshare_response = await client.get(
        f"/api/v1/clothes/{item_id}", headers=auth_headers(friend["access_token"])
    )
    assert after_unshare_response.status_code == 404
