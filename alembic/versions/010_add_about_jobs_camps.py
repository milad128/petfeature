"""add jobs and camps to about_pages

Revision ID: 010
Revises: 009
Create Date: 2026-07-14
"""

from alembic import op
import sqlalchemy as sa

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "about_pages",
        sa.Column("jobs", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "about_pages",
        sa.Column("camps", sa.JSON(), nullable=False, server_default="[]"),
    )


def downgrade() -> None:
    op.drop_column("about_pages", "camps")
    op.drop_column("about_pages", "jobs")
