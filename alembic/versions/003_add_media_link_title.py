"""Add title column to book_media_links."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "003_add_media_link_title"
down_revision: Union[str, None] = "002_drop_buy_links"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in inspect(bind).get_columns("book_media_links")}

    if "title" not in columns:
        op.add_column("book_media_links", sa.Column("title", sa.String(length=300), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in inspect(bind).get_columns("book_media_links")}

    if "title" in columns:
        op.drop_column("book_media_links", "title")
