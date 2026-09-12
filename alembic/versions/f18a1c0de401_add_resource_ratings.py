"""add resource_ratings table

Revision ID: f18a1c0de401
Revises: e17a1b2c3d4e
Create Date: 2026-09-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f18a1c0de401"
down_revision: Union[str, None] = "e17a1b2c3d4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "resource_ratings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("roadmap_resource_id", sa.Integer(), nullable=False),
        sa.Column("stars", sa.SmallInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "stars >= 1 AND stars <= 5",
            name="ck_resource_ratings_stars",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["roadmap_resource_id"],
            ["roadmap_resources.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "roadmap_resource_id",
            name="uq_resource_rating_user_resource",
        ),
    )
    op.create_index(
        op.f("ix_resource_ratings_user_id"),
        "resource_ratings",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_resource_ratings_roadmap_resource_id"),
        "resource_ratings",
        ["roadmap_resource_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_resource_ratings_roadmap_resource_id"),
        table_name="resource_ratings",
    )
    op.drop_index(op.f("ix_resource_ratings_user_id"), table_name="resource_ratings")
    op.drop_table("resource_ratings")
