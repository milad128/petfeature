"""Add show_in_library column to books."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "004_add_show_in_library"
down_revision: Union[str, None] = "003_add_media_link_title"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in inspect(bind).get_columns("books")}

    if "show_in_library" not in columns:
        op.add_column(
            "books",
            sa.Column("show_in_library", sa.Boolean(), nullable=False, server_default=sa.true()),
        )


def downgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in inspect(bind).get_columns("books")}

    if "show_in_library" in columns:
        op.drop_column("books", "show_in_library")
