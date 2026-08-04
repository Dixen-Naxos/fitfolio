from httpx import AsyncClient

from tests.conftest import auth_headers, register_user


async def test_create_and_list_clothing_items(client: AsyncClient) -> None:
    user = await register_user(client, "wardrobe-owner@example.com")
    headers = auth_headers(user["access_token"])

    create_response = await client.post(
        "/api/v1/clothes",
        json={"name": "Blue Jeans", "category": "bottom", "color": "blue", "tags": ["casual"]},
        headers=headers,
    )
    assert create_response.status_code == 201
    item = create_response.json()
    assert item["name"] == "Blue Jeans"
    assert item["image_url"] is None

    list_response = await client.get("/api/v1/clothes", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


async def test_update_and_delete_clothing_item(client: AsyncClient) -> None:
    user = await register_user(client, "wardrobe-editor@example.com")
    headers = auth_headers(user["access_token"])

    create_response = await client.post(
        "/api/v1/clothes",
        json={"name": "White Tee", "category": "top"},
        headers=headers,
    )
    item_id = create_response.json()["id"]

    update_response = await client.patch(
        f"/api/v1/clothes/{item_id}", json={"color": "white"}, headers=headers
    )
    assert update_response.status_code == 200
    assert update_response.json()["color"] == "white"

    delete_response = await client.delete(f"/api/v1/clothes/{item_id}", headers=headers)
    assert delete_response.status_code == 204

    get_response = await client.get(f"/api/v1/clothes/{item_id}", headers=headers)
    assert get_response.status_code == 404


async def test_upload_image_flow(client: AsyncClient) -> None:
    user = await register_user(client, "wardrobe-image@example.com")
    headers = auth_headers(user["access_token"])

    create_response = await client.post(
        "/api/v1/clothes", json={"name": "Sneakers", "category": "shoes"}, headers=headers
    )
    item_id = create_response.json()["id"]

    upload_url_response = await client.post(
        f"/api/v1/clothes/{item_id}/image/upload-url",
        json={"content_type": "image/png"},
        headers=headers,
    )
    assert upload_url_response.status_code == 200
    object_key = upload_url_response.json()["object_key"]
    assert object_key.startswith(f"clothes/{user['user']['id']}/{item_id}/")

    confirm_response = await client.post(
        f"/api/v1/clothes/{item_id}/image/confirm",
        json={"object_key": object_key},
        headers=headers,
    )
    assert confirm_response.status_code == 200
    assert confirm_response.json()["image_url"] is not None


async def test_clothing_item_isolated_between_owners(client: AsyncClient) -> None:
    owner = await register_user(client, "closet-owner@example.com")
    other = await register_user(client, "closet-intruder@example.com")

    create_response = await client.post(
        "/api/v1/clothes",
        json={"name": "Private Jacket", "category": "outerwear"},
        headers=auth_headers(owner["access_token"]),
    )
    item_id = create_response.json()["id"]

    # Another user must not be able to see, edit or delete someone else's item.
    get_response = await client.get(
        f"/api/v1/clothes/{item_id}", headers=auth_headers(other["access_token"])
    )
    assert get_response.status_code == 404

    patch_response = await client.patch(
        f"/api/v1/clothes/{item_id}", json={"name": "Hacked"}, headers=auth_headers(other["access_token"])
    )
    assert patch_response.status_code == 404

    delete_response = await client.delete(
        f"/api/v1/clothes/{item_id}", headers=auth_headers(other["access_token"])
    )
    assert delete_response.status_code == 404

    list_response = await client.get("/api/v1/clothes", headers=auth_headers(other["access_token"]))
    assert list_response.json() == []
