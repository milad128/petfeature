"""add page_views table

Revision ID: 012
Revises: 011
Create Date: 2026-07-14
"""

from alembic import op
import sqlalchemy as sa

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "page_views",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("path", sa.String(500), nullable=False),
        sa.Column("page_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("visitor_token", sa.String(64), nullable=False),
        sa.Column("referrer_domain", sa.String(300), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_page_views_visitor_token", "page_views", ["visitor_token"])
    op.create_index("ix_page_views_created_at", "page_views", ["created_at"])
    op.create_index(
        "ix_page_views_type_entity", "page_views", ["page_type", "entity_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_page_views_type_entity", table_name="page_views")
    op.drop_index("ix_page_views_created_at", table_name="page_views")
    op.drop_index("ix_page_views_visitor_token", table_name="page_views")
    op.drop_table("page_views")
