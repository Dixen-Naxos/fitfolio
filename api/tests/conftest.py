import uuid
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.services import storage_service

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=StaticPool, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(db_engine):
    return async_sessionmaker(bind=db_engine, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
def _stub_storage(monkeypatch):
    """Avoid hitting a real MinIO instance during tests."""

    def fake_upload_url(object_key: str, **kwargs) -> str:
        return f"http://fake-minio.local/upload/{object_key}"

    def fake_view_url(object_key: str, **kwargs) -> str:
        return f"http://fake-minio.local/view/{object_key}"

    def fake_build_object_key(namespace: str, owner_id: uuid.UUID, resource_id: uuid.UUID, content_type: str) -> str:
        return f"{namespace}/{owner_id}/{resource_id}/test.jpg"

    monkeypatch.setattr(storage_service, "presigned_upload_url", fake_upload_url)
    monkeypatch.setattr(storage_service, "presigned_view_url", fake_view_url)
    monkeypatch.setattr(storage_service, "build_object_key", fake_build_object_key)
    monkeypatch.setattr(storage_service, "delete_object", lambda object_key: None)
    monkeypatch.setattr(storage_service, "ensure_bucket", lambda: None)


@pytest_asyncio.fixture
async def client(session_factory) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


async def register_user(client: AsyncClient, email: str, password: str = "password123", display_name: str = "Test User") -> dict:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "display_name": display_name},
    )
    assert response.status_code == 201, response.text
    return response.json()


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
