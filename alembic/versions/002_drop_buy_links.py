"""Replace buy_links JSON with buy_link_title, buy_link_url, download_file."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "002_drop_buy_links"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in inspect(bind).get_columns("books")}

    if "buy_link_title" not in columns:
        op.add_column("books", sa.Column("buy_link_title", sa.String(length=300), nullable=True))
    if "buy_link_url" not in columns:
        op.add_column("books", sa.Column("buy_link_url", sa.String(length=1000), nullable=True))
    if "download_file" not in columns:
        op.add_column("books", sa.Column("download_file", sa.String(length=1000), nullable=True))

    if "buy_links" in columns:
        op.drop_column("books", "buy_links")


def downgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in inspect(bind).get_columns("books")}

    if "buy_links" not in columns:
        op.add_column("books", sa.Column("buy_links", sa.JSON(), nullable=False, server_default="[]"))

    if "download_file" in columns:
        op.drop_column("books", "download_file")
    if "buy_link_url" in columns:
        op.drop_column("books", "buy_link_url")
    if "buy_link_title" in columns:
        op.drop_column("books", "buy_link_title")
