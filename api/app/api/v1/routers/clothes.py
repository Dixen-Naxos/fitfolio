import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from minio.error import S3Error

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.clothing_item import ClothingItem
from app.models.share import ResourceType, Share
from app.models.user import User
from app.schemas.clothing_item import (
    ClothingItemCreate,
    ClothingItemRead,
    ClothingItemUpdate,
    ConfirmImageRequest,
    UploadUrlRequest,
    UploadUrlResponse,
)
from app.services import storage_service

router = APIRouter(prefix="/clothes", tags=["clothes"])


def _to_read(item: ClothingItem) -> ClothingItemRead:
    read = ClothingItemRead.model_validate(item)
    if item.image_key:
        read.image_url = storage_service.presigned_view_url(item.image_key)
    return read


async def _get_owned_item(db: AsyncSession, item_id: uuid.UUID, owner_id: uuid.UUID) -> ClothingItem:
    result = await db.execute(
        select(ClothingItem).where(ClothingItem.id == item_id, ClothingItem.owner_id == owner_id)
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clothing item not found")
    return item


async def _get_accessible_item(db: AsyncSession, item_id: uuid.UUID, user: User) -> ClothingItem:
    result = await db.execute(select(ClothingItem).where(ClothingItem.id == item_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clothing item not found")
    if item.owner_id == user.id:
        return item

    share_result = await db.execute(
        select(Share).where(
            Share.resource_type == ResourceType.clothing_item,
            Share.resource_id == item_id,
            Share.shared_with_id == user.id,
        )
    )
    if share_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clothing item not found")
    return item


@router.get("", response_model=list[ClothingItemRead])
async def list_clothes(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[ClothingItemRead]:
    result = await db.execute(
        select(ClothingItem)
        .where(ClothingItem.owner_id == current_user.id)
        .order_by(ClothingItem.created_at.desc())
    )
    return [_to_read(item) for item in result.scalars().all()]


@router.post("", response_model=ClothingItemRead, status_code=status.HTTP_201_CREATED)
async def create_clothing_item(
    payload: ClothingItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ClothingItemRead:
    item = ClothingItem(owner_id=current_user.id, **payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return _to_read(item)


@router.get("/{item_id}", response_model=ClothingItemRead)
async def get_clothing_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ClothingItemRead:
    item = await _get_accessible_item(db, item_id, current_user)
    return _to_read(item)


@router.patch("/{item_id}", response_model=ClothingItemRead)
async def update_clothing_item(
    item_id: uuid.UUID,
    payload: ClothingItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ClothingItemRead:
    item = await _get_owned_item(db, item_id, current_user.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return _to_read(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_clothing_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    item = await _get_owned_item(db, item_id, current_user.id)

    if item.image_key:
        try:
            storage_service.delete_object(item.image_key)
        except S3Error as exc:
            if exc.code not in {"NoSuchKey", "NoSuchObject"}:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to delete clothing image from storage",
                ) from exc

    await db.delete(item)
    await db.commit()


@router.post("/{item_id}/image/upload-url", response_model=UploadUrlResponse)
async def create_upload_url(
    item_id: uuid.UUID,
    payload: UploadUrlRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UploadUrlResponse:
    item = await _get_owned_item(db, item_id, current_user.id)
    object_key = storage_service.build_object_key("clothes", current_user.id, item.id, payload.content_type)
    upload_url = storage_service.presigned_upload_url(object_key)
    return UploadUrlResponse(upload_url=upload_url, object_key=object_key)


@router.post("/{item_id}/image/confirm", response_model=ClothingItemRead)
async def confirm_image(
    item_id: uuid.UUID,
    payload: ConfirmImageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ClothingItemRead:
    item = await _get_owned_item(db, item_id, current_user.id)
    expected_prefix = f"clothes/{current_user.id}/{item.id}/"
    if not payload.object_key.startswith(expected_prefix):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid object key")
    item.image_key = payload.object_key
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return _to_read(item)
