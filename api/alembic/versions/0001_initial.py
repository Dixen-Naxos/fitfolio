"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-04

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "clothing_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "owner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column(
            "category",
            sa.Enum(
                "top", "bottom", "outerwear", "shoes", "accessory", "dress", "other",
                name="clothing_category",
            ),
            nullable=False,
        ),
        sa.Column("color", sa.String(length=50), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("image_key", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_clothing_items_owner_id", "clothing_items", ["owner_id"])

    op.create_table(
        "outfits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "owner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_outfits_owner_id", "outfits", ["owner_id"])

    op.create_table(
        "outfit_items",
        sa.Column(
            "outfit_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("outfits.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "clothing_item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clothing_items.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    op.create_table(
        "friendships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "requester_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "addressee_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("pending", "accepted", "declined", "blocked", name="friendship_status"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("requester_id", "addressee_id", name="uq_friendship_pair"),
    )
    op.create_index("ix_friendships_requester_id", "friendships", ["requester_id"])
    op.create_index("ix_friendships_addressee_id", "friendships", ["addressee_id"])

    op.create_table(
        "shares",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "resource_type",
            sa.Enum("clothing_item", "outfit", name="share_resource_type"),
            nullable=False,
        ),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "owner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "shared_with_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint(
            "resource_type", "resource_id", "shared_with_id", name="uq_share_resource_user"
        ),
    )
    op.create_index("ix_shares_resource_id", "shares", ["resource_id"])
    op.create_index("ix_shares_owner_id", "shares", ["owner_id"])
    op.create_index("ix_shares_shared_with_id", "shares", ["shared_with_id"])

    op.create_table(
        "revoked_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("jti", sa.String(length=36), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_revoked_tokens_jti", "revoked_tokens", ["jti"], unique=True)


def downgrade() -> None:
    op.drop_table("revoked_tokens")
    op.drop_table("shares")
    op.drop_table("friendships")
    op.drop_table("outfit_items")
    op.drop_table("outfits")
    op.drop_table("clothing_items")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS share_resource_type")
    op.execute("DROP TYPE IF EXISTS friendship_status")
    op.execute("DROP TYPE IF EXISTS clothing_category")
