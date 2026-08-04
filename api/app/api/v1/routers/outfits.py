import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.clothing_item import ClothingItem
from app.models.outfit import Outfit
from app.models.outfit_item import OutfitItem
from app.models.share import ResourceType, Share
from app.models.user import User
from app.schemas.outfit import OutfitCreate, OutfitRead, OutfitUpdate, SetOutfitItemsRequest
from app.services.storage_service import presigned_view_url

router = APIRouter(prefix="/outfits", tags=["outfits"])

_OUTFIT_LOAD_OPTIONS = (selectinload(Outfit.item_links).selectinload(OutfitItem.clothing_item),)


def _to_read(outfit: Outfit) -> OutfitRead:
    read = OutfitRead.model_validate(
        {
            "id": outfit.id,
            "owner_id": outfit.owner_id,
            "name": outfit.name,
            "created_at": outfit.created_at,
            "items": [link.clothing_item for link in outfit.item_links],
        }
    )
    for item in read.items:
        if item.image_url is None:
            source = next(
                (
                    link.clothing_item
                    for link in outfit.item_links
                    if link.clothing_item.id == item.id
                ),
                None,
            )
            if source and source.image_key:
                item.image_url = presigned_view_url(source.image_key)
    return read


async def _get_owned_outfit(db: AsyncSession, outfit_id: uuid.UUID, owner_id: uuid.UUID) -> Outfit:
    result = await db.execute(
        select(Outfit)
        .options(*_OUTFIT_LOAD_OPTIONS)
        .where(Outfit.id == outfit_id, Outfit.owner_id == owner_id)
        .execution_options(populate_existing=True)
    )
    outfit = result.scalar_one_or_none()
    if outfit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")
    return outfit


async def _get_accessible_outfit(db: AsyncSession, outfit_id: uuid.UUID, user: User) -> Outfit:
    result = await db.execute(
        select(Outfit)
        .options(*_OUTFIT_LOAD_OPTIONS)
        .where(Outfit.id == outfit_id)
        .execution_options(populate_existing=True)
    )
    outfit = result.scalar_one_or_none()
    if outfit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")
    if outfit.owner_id == user.id:
        return outfit

    share_result = await db.execute(
        select(Share).where(
            Share.resource_type == ResourceType.outfit,
            Share.resource_id == outfit_id,
            Share.shared_with_id == user.id,
        )
    )
    if share_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")
    return outfit


@router.get("", response_model=list[OutfitRead])
async def list_outfits(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[OutfitRead]:
    result = await db.execute(
        select(Outfit)
        .options(*_OUTFIT_LOAD_OPTIONS)
        .where(Outfit.owner_id == current_user.id)
        .order_by(Outfit.created_at.desc())
    )
    return [_to_read(outfit) for outfit in result.scalars().unique().all()]


@router.post("", response_model=OutfitRead, status_code=status.HTTP_201_CREATED)
async def create_outfit(
    payload: OutfitCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OutfitRead:
    outfit = Outfit(owner_id=current_user.id, name=payload.name)
    db.add(outfit)
    await db.commit()
    outfit = await _get_owned_outfit(db, outfit.id, current_user.id)
    return _to_read(outfit)


@router.get("/{outfit_id}", response_model=OutfitRead)
async def get_outfit(
    outfit_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OutfitRead:
    outfit = await _get_accessible_outfit(db, outfit_id, current_user)
    return _to_read(outfit)


@router.patch("/{outfit_id}", response_model=OutfitRead)
async def update_outfit(
    outfit_id: uuid.UUID,
    payload: OutfitUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OutfitRead:
    outfit = await _get_owned_outfit(db, outfit_id, current_user.id)
    if payload.name is not None:
        outfit.name = payload.name
    db.add(outfit)
    await db.commit()
    outfit = await _get_owned_outfit(db, outfit_id, current_user.id)
    return _to_read(outfit)


@router.delete("/{outfit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_outfit(
    outfit_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    outfit = await _get_owned_outfit(db, outfit_id, current_user.id)
    await db.delete(outfit)
    await db.commit()


@router.put("/{outfit_id}/items", response_model=OutfitRead)
async def set_outfit_items(
    outfit_id: uuid.UUID,
    payload: SetOutfitItemsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OutfitRead:
    outfit = await _get_owned_outfit(db, outfit_id, current_user.id)

    unique_ids = set(payload.clothing_item_ids)
    if unique_ids:
        owned_result = await db.execute(
            select(ClothingItem.id).where(
                ClothingItem.id.in_(unique_ids), ClothingItem.owner_id == current_user.id
            )
        )
        owned_ids = {row[0] for row in owned_result.all()}
        missing = unique_ids - owned_ids
        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Clothing items not found or not owned: {sorted(str(i) for i in missing)}",
            )

    await db.execute(OutfitItem.__table__.delete().where(OutfitItem.outfit_id == outfit_id))
    for clothing_item_id in unique_ids:
        db.add(OutfitItem(outfit_id=outfit_id, clothing_item_id=clothing_item_id))
    await db.commit()

    outfit = await _get_owned_outfit(db, outfit_id, current_user.id)
    return _to_read(outfit)
