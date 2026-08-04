import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.clothing_item import ClothingItem
from app.models.friendship import Friendship, FriendshipStatus
from app.models.outfit import Outfit
from app.models.outfit_item import OutfitItem
from app.models.share import ResourceType, Share
from app.models.user import User
from app.schemas.share import ShareCreate, ShareRead, SharedClothingItem, SharedOutfit, SharedWithMeResponse
from app.services.storage_service import presigned_view_url

router = APIRouter(tags=["sharing"])


async def _are_friends(db: AsyncSession, user_a: uuid.UUID, user_b: uuid.UUID) -> bool:
    result = await db.execute(
        select(Friendship).where(
            Friendship.status == FriendshipStatus.accepted,
            or_(
                (Friendship.requester_id == user_a) & (Friendship.addressee_id == user_b),
                (Friendship.requester_id == user_b) & (Friendship.addressee_id == user_a),
            ),
        )
    )
    return result.scalar_one_or_none() is not None


async def _create_share(
    db: AsyncSession,
    current_user: User,
    resource_type: ResourceType,
    resource_id: uuid.UUID,
    payload: ShareCreate,
) -> Share:
    target_result = await db.execute(select(User).where(User.email == payload.shared_with_email))
    target = target_result.scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if target.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot share with yourself")
    if not await _are_friends(db, current_user.id, target.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You can only share with accepted friends"
        )

    existing = await db.execute(
        select(Share).where(
            Share.resource_type == resource_type,
            Share.resource_id == resource_id,
            Share.shared_with_id == target.id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already shared with this user")

    share = Share(
        resource_type=resource_type,
        resource_id=resource_id,
        owner_id=current_user.id,
        shared_with_id=target.id,
    )
    db.add(share)
    await db.commit()
    await db.refresh(share)
    return share


async def _delete_share(
    db: AsyncSession,
    current_user: User,
    resource_type: ResourceType,
    resource_id: uuid.UUID,
    shared_with_id: uuid.UUID,
) -> None:
    result = await db.execute(
        select(Share).where(
            Share.resource_type == resource_type,
            Share.resource_id == resource_id,
            Share.shared_with_id == shared_with_id,
            Share.owner_id == current_user.id,
        )
    )
    share = result.scalar_one_or_none()
    if share is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share not found")
    await db.delete(share)
    await db.commit()


async def _get_owned_clothing_item(db: AsyncSession, item_id: uuid.UUID, owner_id: uuid.UUID) -> ClothingItem:
    result = await db.execute(
        select(ClothingItem).where(ClothingItem.id == item_id, ClothingItem.owner_id == owner_id)
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clothing item not found")
    return item


async def _get_owned_outfit(db: AsyncSession, outfit_id: uuid.UUID, owner_id: uuid.UUID) -> Outfit:
    result = await db.execute(
        select(Outfit).where(Outfit.id == outfit_id, Outfit.owner_id == owner_id)
    )
    outfit = result.scalar_one_or_none()
    if outfit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")
    return outfit


@router.post("/clothes/{item_id}/share", response_model=ShareRead, status_code=status.HTTP_201_CREATED)
async def share_clothing_item(
    item_id: uuid.UUID,
    payload: ShareCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ShareRead:
    await _get_owned_clothing_item(db, item_id, current_user.id)
    share = await _create_share(db, current_user, ResourceType.clothing_item, item_id, payload)
    return ShareRead.model_validate(share)


@router.delete("/clothes/{item_id}/share/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unshare_clothing_item(
    item_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await _get_owned_clothing_item(db, item_id, current_user.id)
    await _delete_share(db, current_user, ResourceType.clothing_item, item_id, user_id)


@router.post("/outfits/{outfit_id}/share", response_model=ShareRead, status_code=status.HTTP_201_CREATED)
async def share_outfit(
    outfit_id: uuid.UUID,
    payload: ShareCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ShareRead:
    await _get_owned_outfit(db, outfit_id, current_user.id)
    share = await _create_share(db, current_user, ResourceType.outfit, outfit_id, payload)
    return ShareRead.model_validate(share)


@router.delete("/outfits/{outfit_id}/share/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unshare_outfit(
    outfit_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await _get_owned_outfit(db, outfit_id, current_user.id)
    await _delete_share(db, current_user, ResourceType.outfit, outfit_id, user_id)


@router.get("/shared-with-me", response_model=SharedWithMeResponse)
async def shared_with_me(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> SharedWithMeResponse:
    shares_result = await db.execute(select(Share).where(Share.shared_with_id == current_user.id))
    shares = shares_result.scalars().all()

    clothing_items: list[SharedClothingItem] = []
    outfits: list[SharedOutfit] = []

    for share in shares:
        if share.resource_type == ResourceType.clothing_item:
            item_result = await db.execute(
                select(ClothingItem).where(ClothingItem.id == share.resource_id)
            )
            item = item_result.scalar_one_or_none()
            if item is None:
                continue
            image_url = presigned_view_url(item.image_key) if item.image_key else None
            item_read = {
                "id": item.id,
                "owner_id": item.owner_id,
                "name": item.name,
                "category": item.category,
                "color": item.color,
                "tags": item.tags,
                "image_url": image_url,
                "created_at": item.created_at,
            }
            clothing_items.append(
                SharedClothingItem(share=ShareRead.model_validate(share), clothing_item=item_read)
            )
        else:
            outfit_result = await db.execute(
                select(Outfit).where(Outfit.id == share.resource_id)
            )
            outfit = outfit_result.scalar_one_or_none()
            if outfit is None:
                continue
            links_result = await db.execute(
                select(OutfitItem).where(OutfitItem.outfit_id == outfit.id)
            )
            links = links_result.scalars().all()
            items = []
            for link in links:
                ci_result = await db.execute(
                    select(ClothingItem).where(ClothingItem.id == link.clothing_item_id)
                )
                ci = ci_result.scalar_one_or_none()
                if ci is None:
                    continue
                items.append(
                    {
                        "id": ci.id,
                        "owner_id": ci.owner_id,
                        "name": ci.name,
                        "category": ci.category,
                        "color": ci.color,
                        "tags": ci.tags,
                        "image_url": presigned_view_url(ci.image_key) if ci.image_key else None,
                        "created_at": ci.created_at,
                    }
                )
            outfit_read = {
                "id": outfit.id,
                "owner_id": outfit.owner_id,
                "name": outfit.name,
                "created_at": outfit.created_at,
                "items": items,
            }
            outfits.append(SharedOutfit(share=ShareRead.model_validate(share), outfit=outfit_read))

    return SharedWithMeResponse(clothing_items=clothing_items, outfits=outfits)
