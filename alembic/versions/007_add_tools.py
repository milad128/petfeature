"""Add tools (template library): tools, tool_files, tool_books, tool_posts."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007_add_tools"
down_revision: Union[str, None] = "006_add_blog"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tools",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("slug", sa.String(length=200), nullable=False),
        sa.Column("cover", sa.String(length=1000), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("short_description", sa.String(length=500), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_tools_slug"), "tools", ["slug"], unique=True)

    op.create_table(
        "tool_files",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tool_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("file", sa.String(length=1000), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["tool_id"], ["tools.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "tool_books",
        sa.Column("tool_id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["tool_id"], ["tools.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tool_id", "book_id"),
    )

    op.create_table(
        "tool_posts",
        sa.Column("tool_id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["tool_id"], ["tools.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tool_id", "post_id"),
    )


def downgrade() -> None:
    op.drop_table("tool_posts")
    op.drop_table("tool_books")
    op.drop_table("tool_files")
    op.drop_index(op.f("ix_tools_slug"), table_name="tools")
    op.drop_table("tools")
