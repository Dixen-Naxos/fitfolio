from httpx import AsyncClient
from app.services import storage_service

from tests.conftest import auth_headers, register_user


async def test_create_and_list_clothing_items(client: AsyncClient) -> None:
    user = await register_user(client, "wardrobe-owner@example.com")
    headers = auth_headers(user["access_token"])

    create_response = await client.post(
        "/api/v1/clothes",
        json={
            "name": "Blue Jeans",
            "category": "bottom",
            "subcategory": "Jean",
            "color": "blue",
            "tags": ["casual"],
        },
        headers=headers,
    )
    assert create_response.status_code == 201
    item = create_response.json()
    assert item["name"] == "Blue Jeans"
    assert item["subcategory"] == "Jean"
    assert item["image_url"] is None

    list_response = await client.get("/api/v1/clothes", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    lingerie_response = await client.post(
        "/api/v1/clothes",
        json={"name": "Black Bra", "category": "lingerie", "subcategory": "Brassières"},
        headers=headers,
    )
    assert lingerie_response.status_code == 201
    assert lingerie_response.json()["category"] == "lingerie"
    assert lingerie_response.json()["subcategory"] == "Brassières"


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


async def test_delete_clothing_item_removes_image_object(client: AsyncClient, monkeypatch) -> None:
    user = await register_user(client, "wardrobe-delete-image@example.com")
    headers = auth_headers(user["access_token"])

    create_response = await client.post(
        "/api/v1/clothes",
        json={"name": "Hat", "category": "accessory"},
        headers=headers,
    )
    item_id = create_response.json()["id"]

    upload_url_response = await client.post(
        f"/api/v1/clothes/{item_id}/image/upload-url",
        json={"content_type": "image/png"},
        headers=headers,
    )
    object_key = upload_url_response.json()["object_key"]

    confirm_response = await client.post(
        f"/api/v1/clothes/{item_id}/image/confirm",
        json={"object_key": object_key},
        headers=headers,
    )
    assert confirm_response.status_code == 200

    deleted_keys: list[str] = []

    def fake_delete_object(key: str) -> None:
        deleted_keys.append(key)

    monkeypatch.setattr(storage_service, "delete_object", fake_delete_object)

    delete_response = await client.delete(f"/api/v1/clothes/{item_id}", headers=headers)
    assert delete_response.status_code == 204
    assert deleted_keys == [object_key]


async def test_upload_url_rejects_unsupported_content_type(client: AsyncClient) -> None:
    user = await register_user(client, "wardrobe-badtype@example.com")
    headers = auth_headers(user["access_token"])

    create_response = await client.post(
        "/api/v1/clothes", json={"name": "Boots", "category": "shoes"}, headers=headers
    )
    item_id = create_response.json()["id"]

    response = await client.post(
        f"/api/v1/clothes/{item_id}/image/upload-url",
        json={"content_type": "application/pdf"},
        headers=headers,
    )
    assert response.status_code == 415


async def test_upload_url_accepts_png(client: AsyncClient) -> None:
    user = await register_user(client, "wardrobe-png@example.com")
    headers = auth_headers(user["access_token"])

    create_response = await client.post(
        "/api/v1/clothes", json={"name": "Scarf", "category": "accessory"}, headers=headers
    )
    item_id = create_response.json()["id"]

    response = await client.post(
        f"/api/v1/clothes/{item_id}/image/upload-url",
        json={"content_type": "image/png"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["object_key"].endswith(".png")


async def test_confirm_rejects_missing_object(client: AsyncClient, monkeypatch) -> None:
    from minio.error import S3Error

    user = await register_user(client, "wardrobe-missing@example.com")
    headers = auth_headers(user["access_token"])

    create_response = await client.post(
        "/api/v1/clothes", json={"name": "Cap", "category": "accessory"}, headers=headers
    )
    item_id = create_response.json()["id"]
    object_key = f"clothes/{user['user']['id']}/{item_id}/test.png"

    def raise_missing(key: str):
        raise S3Error("NoSuchKey", "not found", key, "req", "host", None)

    monkeypatch.setattr(storage_service, "stat_object", raise_missing)

    response = await client.post(
        f"/api/v1/clothes/{item_id}/image/confirm",
        json={"object_key": object_key},
        headers=headers,
    )
    assert response.status_code == 400


async def test_confirm_rejects_wrong_mime(client: AsyncClient, monkeypatch) -> None:
    from types import SimpleNamespace

    user = await register_user(client, "wardrobe-wrongmime@example.com")
    headers = auth_headers(user["access_token"])

    create_response = await client.post(
        "/api/v1/clothes", json={"name": "Gloves", "category": "accessory"}, headers=headers
    )
    item_id = create_response.json()["id"]
    object_key = f"clothes/{user['user']['id']}/{item_id}/test.png"

    deleted: list[str] = []
    monkeypatch.setattr(
        storage_service, "stat_object", lambda key: SimpleNamespace(content_type="application/pdf", size=1024)
    )
    monkeypatch.setattr(storage_service, "delete_object", lambda key: deleted.append(key))

    response = await client.post(
        f"/api/v1/clothes/{item_id}/image/confirm",
        json={"object_key": object_key},
        headers=headers,
    )
    assert response.status_code == 400
    # The junk object should have been cleaned up.
    assert deleted == [object_key]


async def test_confirm_rejects_oversized_object(client: AsyncClient, monkeypatch) -> None:
    from types import SimpleNamespace

    from app.core.config import settings

    user = await register_user(client, "wardrobe-oversize@example.com")
    headers = auth_headers(user["access_token"])

    create_response = await client.post(
        "/api/v1/clothes", json={"name": "Coat", "category": "outerwear"}, headers=headers
    )
    item_id = create_response.json()["id"]
    object_key = f"clothes/{user['user']['id']}/{item_id}/test.png"

    too_big = settings.max_upload_size_bytes + 1
    monkeypatch.setattr(
        storage_service, "stat_object", lambda key: SimpleNamespace(content_type="image/png", size=too_big)
    )
    monkeypatch.setattr(storage_service, "delete_object", lambda key: None)

    response = await client.post(
        f"/api/v1/clothes/{item_id}/image/confirm",
        json={"object_key": object_key},
        headers=headers,
    )
    assert response.status_code == 400
