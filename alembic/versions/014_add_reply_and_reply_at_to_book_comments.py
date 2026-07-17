"""add reply and reply_at to book_comments

Revision ID: b014bookreply01
Revises: ac10bfb954ef
Create Date: 2026-07-17 16:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b014bookreply01"
down_revision: Union[str, None] = "ac10bfb954ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("book_comments", sa.Column("reply", sa.Text(), nullable=True))
    op.add_column("book_comments", sa.Column("reply_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("book_comments", "reply_at")
    op.drop_column("book_comments", "reply")
