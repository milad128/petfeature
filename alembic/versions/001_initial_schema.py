"""Initial schema: books with refined attributes."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cover", sa.String(length=1000), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("subtitle", sa.String(length=500), nullable=True),
        sa.Column("authors", sa.JSON(), nullable=False),
        sa.Column("published_year", sa.Integer(), nullable=True),
        sa.Column("slug", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("labels", sa.JSON(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("quotes", sa.JSON(), nullable=False),
        sa.Column("buy_link_title", sa.String(length=300), nullable=True),
        sa.Column("buy_link_url", sa.String(length=1000), nullable=True),
        sa.Column("download_file", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_books_slug"), "books", ["slug"], unique=True)

    op.create_table(
        "book_media_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "book_references",
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("referred_book_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["referred_book_id"], ["books.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("book_id", "referred_book_id"),
    )

    op.create_table(
        "about_pages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("author_name", sa.String(length=200), nullable=False),
        sa.Column("author_photo", sa.String(length=1000), nullable=True),
        sa.Column("author_bio", sa.Text(), nullable=True),
        sa.Column("pet_feature_body", sa.Text(), nullable=True),
        sa.Column("site_story_body", sa.Text(), nullable=True),
        sa.Column("links", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("about_pages")
    op.drop_table("book_references")
    op.drop_table("book_media_links")
    op.drop_index(op.f("ix_books_slug"), table_name="books")
    op.drop_table("books")
