import uuid
from datetime import timedelta

from minio import Minio
from minio.datatypes import Object
from minio.error import S3Error

from app.core.config import settings

# Content types we accept for image uploads, mapped to the extension used in the object key.
# This is the single source of truth: reject anything not listed instead of silently
# coercing to a default extension.
ALLOWED_CONTENT_TYPES: dict[str, str] = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/heic": "heic",
}

_client: Minio | None = None
_presign_client: Minio | None = None


def is_allowed_content_type(content_type: str | None) -> bool:
    return content_type in ALLOWED_CONTENT_TYPES


def extension_for(content_type: str) -> str:
    """Extension for an allowed content type. Raises KeyError for unsupported types."""
    return ALLOWED_CONTENT_TYPES[content_type]


def get_client() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
            region=settings.minio_region,
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
            region=settings.minio_region,
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
    """Build an object key for an allowed content type.

    Raises KeyError for unsupported content types; callers must validate with
    is_allowed_content_type first and reject the request.
    """
    extension = extension_for(content_type)
    return f"{namespace}/{owner_id}/{resource_id}/{uuid.uuid4()}.{extension}"


def presigned_upload_url(object_key: str, expires: timedelta = timedelta(minutes=10)) -> str:
    client = get_presign_client()
    return client.presigned_put_object(settings.minio_bucket, object_key, expires=expires)


def presigned_view_url(object_key: str, expires: timedelta = timedelta(hours=1)) -> str:
    client = get_presign_client()
    return client.presigned_get_object(settings.minio_bucket, object_key, expires=expires)


def stat_object(object_key: str) -> Object:
    """Return object metadata (size, content_type, ...). Raises S3Error if missing."""
    client = get_client()
    return client.stat_object(settings.minio_bucket, object_key)


def delete_object(object_key: str) -> None:
    client = get_client()
    client.remove_object(settings.minio_bucket, object_key)
