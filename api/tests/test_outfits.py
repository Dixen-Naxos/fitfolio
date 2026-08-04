from httpx import AsyncClient

from tests.conftest import auth_headers, register_user


async def _create_clothing_item(client: AsyncClient, headers: dict, name: str, category: str = "top") -> str:
    response = await client.post(
        "/api/v1/clothes", json={"name": name, "category": category}, headers=headers
    )
    assert response.status_code == 201
    return response.json()["id"]


async def test_create_outfit_and_set_items(client: AsyncClient) -> None:
    user = await register_user(client, "outfit-owner@example.com")
    headers = auth_headers(user["access_token"])

    top_id = await _create_clothing_item(client, headers, "Tee", "top")
    bottom_id = await _create_clothing_item(client, headers, "Jeans", "bottom")

    create_response = await client.post("/api/v1/outfits", json={"name": "Casual Friday"}, headers=headers)
    assert create_response.status_code == 201
    outfit_id = create_response.json()["id"]
    assert create_response.json()["items"] == []

    set_items_response = await client.put(
        f"/api/v1/outfits/{outfit_id}/items",
        json={"clothing_item_ids": [top_id, bottom_id]},
        headers=headers,
    )
    assert set_items_response.status_code == 200
    item_ids = {item["id"] for item in set_items_response.json()["items"]}
    assert item_ids == {top_id, bottom_id}


async def test_cannot_add_others_clothing_item_to_outfit(client: AsyncClient) -> None:
    owner = await register_user(client, "outfit-owner2@example.com")
    other = await register_user(client, "outfit-stranger@example.com")

    owner_headers = auth_headers(owner["access_token"])
    other_item_id = await _create_clothing_item(client, auth_headers(other["access_token"]), "Stranger Shirt")

    create_response = await client.post("/api/v1/outfits", json={"name": "Weekend"}, headers=owner_headers)
    outfit_id = create_response.json()["id"]

    set_items_response = await client.put(
        f"/api/v1/outfits/{outfit_id}/items",
        json={"clothing_item_ids": [other_item_id]},
        headers=owner_headers,
    )
    assert set_items_response.status_code == 400


async def test_delete_outfit(client: AsyncClient) -> None:
    user = await register_user(client, "outfit-delete@example.com")
    headers = auth_headers(user["access_token"])

    create_response = await client.post("/api/v1/outfits", json={"name": "To Delete"}, headers=headers)
    outfit_id = create_response.json()["id"]

    delete_response = await client.delete(f"/api/v1/outfits/{outfit_id}", headers=headers)
    assert delete_response.status_code == 204

    get_response = await client.get(f"/api/v1/outfits/{outfit_id}", headers=headers)
    assert get_response.status_code == 404
