import uuid
from datetime import timedelta

from minio import Minio
from minio.error import S3Error

from app.core.config import settings

_ALLOWED_CONTENT_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/heic": "heic",
}
DEFAULT_EXTENSION = "jpg"

_client: Minio | None = None
_presign_client: Minio | None = None


def get_client() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
    return _client


def get_presign_client() -> Minio:
    global _presign_client
    if _presign_client is None:
        endpoint = settings.minio_presign_endpoint or settings.minio_endpoint
        secure = settings.minio_presign_secure
        if secure is None:
            secure = settings.minio_secure

        _presign_client = Minio(
            endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=secure,
        )
    return _presign_client


def ensure_bucket() -> None:
    client = get_client()
    try:
        if not client.bucket_exists(settings.minio_bucket):
            client.make_bucket(settings.minio_bucket)
    except S3Error:
        # Best-effort at startup; individual requests will surface real errors.
        pass


def build_object_key(namespace: str, owner_id: uuid.UUID, resource_id: uuid.UUID, content_type: str) -> str:
    extension = _ALLOWED_CONTENT_TYPES.get(content_type, DEFAULT_EXTENSION)
    return f"{namespace}/{owner_id}/{resource_id}/{uuid.uuid4()}.{extension}"


def presigned_upload_url(object_key: str, expires: timedelta = timedelta(minutes=10)) -> str:
    client = get_presign_client()
    return client.presigned_put_object(settings.minio_bucket, object_key, expires=expires)


def presigned_view_url(object_key: str, expires: timedelta = timedelta(hours=1)) -> str:
    client = get_presign_client()
    return client.presigned_get_object(settings.minio_bucket, object_key, expires=expires)


def delete_object(object_key: str) -> None:
    client = get_client()
    client.remove_object(settings.minio_bucket, object_key)
