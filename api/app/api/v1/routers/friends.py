import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.friendship import Friendship, FriendshipStatus
from app.models.user import User
from app.schemas.friendship import FriendRead, FriendRequestCreate, FriendshipRead
from app.schemas.user import UserRead

router = APIRouter(prefix="/friends", tags=["friends"])


@router.post("/requests", response_model=FriendshipRead, status_code=status.HTTP_201_CREATED)
async def send_friend_request(
    payload: FriendRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FriendshipRead:
    result = await db.execute(select(User).where(User.email == payload.addressee_email))
    addressee = result.scalar_one_or_none()
    if addressee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if addressee.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot send a friend request to yourself"
        )

    existing = await db.execute(
        select(Friendship).where(
            or_(
                (Friendship.requester_id == current_user.id) & (Friendship.addressee_id == addressee.id),
                (Friendship.requester_id == addressee.id) & (Friendship.addressee_id == current_user.id),
            )
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="A friendship or request already exists"
        )

    friendship = Friendship(requester_id=current_user.id, addressee_id=addressee.id)
    db.add(friendship)
    await db.commit()
    await db.refresh(friendship)
    return FriendshipRead.model_validate(friendship)


@router.get("/requests", response_model=list[FriendshipRead])
async def list_friend_requests(
    direction: Literal["incoming", "outgoing"] | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[FriendshipRead]:
    conditions = [Friendship.status == FriendshipStatus.pending]
    if direction == "incoming":
        conditions.append(Friendship.addressee_id == current_user.id)
    elif direction == "outgoing":
        conditions.append(Friendship.requester_id == current_user.id)
    else:
        conditions.append(
            or_(Friendship.addressee_id == current_user.id, Friendship.requester_id == current_user.id)
        )

    result = await db.execute(select(Friendship).where(*conditions))
    return [FriendshipRead.model_validate(f) for f in result.scalars().all()]


async def _get_incoming_request(db: AsyncSession, friendship_id: uuid.UUID, user: User) -> Friendship:
    result = await db.execute(
        select(Friendship).where(
            Friendship.id == friendship_id,
            Friendship.addressee_id == user.id,
            Friendship.status == FriendshipStatus.pending,
        )
    )
    friendship = result.scalar_one_or_none()
    if friendship is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friend request not found")
    return friendship


@router.post("/requests/{friendship_id}/accept", response_model=FriendshipRead)
async def accept_friend_request(
    friendship_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FriendshipRead:
    friendship = await _get_incoming_request(db, friendship_id, current_user)
    friendship.status = FriendshipStatus.accepted
    db.add(friendship)
    await db.commit()
    await db.refresh(friendship)
    return FriendshipRead.model_validate(friendship)


@router.post("/requests/{friendship_id}/decline", response_model=FriendshipRead)
async def decline_friend_request(
    friendship_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FriendshipRead:
    friendship = await _get_incoming_request(db, friendship_id, current_user)
    friendship.status = FriendshipStatus.declined
    db.add(friendship)
    await db.commit()
    await db.refresh(friendship)
    return FriendshipRead.model_validate(friendship)


@router.get("", response_model=list[FriendRead])
async def list_friends(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[FriendRead]:
    result = await db.execute(
        select(Friendship).where(
            Friendship.status == FriendshipStatus.accepted,
            or_(Friendship.requester_id == current_user.id, Friendship.addressee_id == current_user.id),
        )
    )
    friendships = result.scalars().all()

    friends: list[FriendRead] = []
    for friendship in friendships:
        other_id = (
            friendship.addressee_id
            if friendship.requester_id == current_user.id
            else friendship.requester_id
        )
        other_result = await db.execute(select(User).where(User.id == other_id))
        other = other_result.scalar_one_or_none()
        if other is not None:
            friends.append(FriendRead(friendship_id=friendship.id, user=UserRead.model_validate(other)))
    return friends


@router.delete("/{friendship_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_friend(
    friendship_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(Friendship).where(
            Friendship.id == friendship_id,
            or_(Friendship.requester_id == current_user.id, Friendship.addressee_id == current_user.id),
        )
    )
    friendship = result.scalar_one_or_none()
    if friendship is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friendship not found")
    await db.delete(friendship)
    await db.commit()
