"""Replace freeform book labels with managed categories."""

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect, table, column

revision: str = "005_add_categories"
down_revision: Union[str, None] = "004_add_show_in_library"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "categories" not in existing_tables:
        op.create_table(
            "categories",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name"),
        )

    if "book_categories" not in existing_tables:
        op.create_table(
            "book_categories",
            sa.Column("book_id", sa.Integer(), nullable=False),
            sa.Column("category_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("book_id", "category_id"),
        )

    columns = {column_info["name"] for column_info in inspect(bind).get_columns("books")}
    if "labels" in columns:
        _migrate_labels_to_categories(bind)
        op.drop_column("books", "labels")


def _migrate_labels_to_categories(bind) -> None:
    books_t = table("books", column("id", sa.Integer), column("labels", sa.JSON))
    categories_t = table("categories", column("id", sa.Integer), column("name", sa.String))
    book_categories_t = table(
        "book_categories", column("book_id", sa.Integer), column("category_id", sa.Integer)
    )

    rows = bind.execute(sa.select(books_t.c.id, books_t.c.labels)).fetchall()
    name_to_id = {
        row.name: row.id for row in bind.execute(sa.select(categories_t.c.id, categories_t.c.name)).fetchall()
    }

    for book_id, raw_labels in rows:
        labels = raw_labels if isinstance(raw_labels, list) else json.loads(raw_labels or "[]")
        for label in labels:
            label = str(label).strip()
            if not label:
                continue
            category_id = name_to_id.get(label)
            if category_id is None:
                result = bind.execute(categories_t.insert().values(name=label))
                category_id = result.inserted_primary_key[0]
                name_to_id[label] = category_id
            exists = bind.execute(
                sa.select(book_categories_t.c.book_id).where(
                    book_categories_t.c.book_id == book_id,
                    book_categories_t.c.category_id == category_id,
                )
            ).first()
            if not exists:
                bind.execute(
                    book_categories_t.insert().values(book_id=book_id, category_id=category_id)
                )


def downgrade() -> None:
    bind = op.get_bind()
    columns = {column_info["name"] for column_info in inspect(bind).get_columns("books")}

    if "labels" not in columns:
        op.add_column("books", sa.Column("labels", sa.JSON(), nullable=False, server_default="[]"))

    op.drop_table("book_categories")
    op.drop_table("categories")
