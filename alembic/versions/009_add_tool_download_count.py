"""add tool download_count

Revision ID: 009
Revises: 008
Create Date: 2026-07-11
"""

from alembic import op
import sqlalchemy as sa

revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tools",
        sa.Column(
            "download_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("tools", "download_count")
