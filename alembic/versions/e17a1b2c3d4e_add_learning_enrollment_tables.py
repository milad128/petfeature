"""add enrollments and resource_progress tables

Revision ID: e17a1b2c3d4e
Revises: 346719cfd0d5
Create Date: 2026-09-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e17a1b2c3d4e"
down_revision: Union[str, None] = "346719cfd0d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "enrollments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("level_slug", sa.String(length=20), nullable=False),
        sa.Column(
            "enrolled_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("unenrolled_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "level_slug", name="uq_enrollment_user_level"),
    )
    op.create_index(op.f("ix_enrollments_user_id"), "enrollments", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_enrollments_level_slug"), "enrollments", ["level_slug"], unique=False
    )

    op.create_table(
        "resource_progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("enrollment_id", sa.Integer(), nullable=False),
        sa.Column("roadmap_resource_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["enrollment_id"], ["enrollments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["roadmap_resource_id"], ["roadmap_resources.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "enrollment_id",
            "roadmap_resource_id",
            name="uq_progress_enrollment_resource",
        ),
    )
    op.create_index(
        op.f("ix_resource_progress_enrollment_id"),
        "resource_progress",
        ["enrollment_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_resource_progress_roadmap_resource_id"),
        "resource_progress",
        ["roadmap_resource_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_resource_progress_roadmap_resource_id"),
        table_name="resource_progress",
    )
    op.drop_index(
        op.f("ix_resource_progress_enrollment_id"), table_name="resource_progress"
    )
    op.drop_table("resource_progress")
    op.drop_index(op.f("ix_enrollments_level_slug"), table_name="enrollments")
    op.drop_index(op.f("ix_enrollments_user_id"), table_name="enrollments")
    op.drop_table("enrollments")
