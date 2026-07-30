"""add_user_id_to_post_comments_and_book_comments

Revision ID: 29be8a288138
Revises: 3a0c3ad75e4f
Create Date: 2026-07-31 01:48:17.968722

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '29be8a288138'
down_revision: Union[str, None] = '3a0c3ad75e4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_sqlite() -> bool:
    bind = op.get_context().bind
    return bind is not None and bind.dialect.name == "sqlite"


def upgrade() -> None:
    # book_comments.user_id
    if not _is_sqlite():
        op.add_column('book_comments', sa.Column('user_id', sa.Integer(), nullable=True))
        op.create_index(op.f('ix_book_comments_user_id'), 'book_comments', ['user_id'], unique=False)
        op.create_foreign_key(None, 'book_comments', 'users', ['user_id'], ['id'], ondelete='SET NULL')
    else:
        # Column may already exist (partially applied in prior attempt)
        try:
            op.add_column('book_comments', sa.Column('user_id', sa.Integer(), nullable=True))
        except Exception:
            pass  # already exists
        try:
            op.create_index(op.f('ix_book_comments_user_id'), 'book_comments', ['user_id'], unique=False)
        except Exception:
            pass
        # FK constraints not supported via ALTER in SQLite — skipped; column semantics are preserved

    # post_comments.user_id
    op.add_column('post_comments', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_post_comments_user_id'), 'post_comments', ['user_id'], unique=False)
    if not _is_sqlite():
        op.create_foreign_key(None, 'post_comments', 'users', ['user_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    if not _is_sqlite():
        op.drop_constraint(None, 'post_comments', type_='foreignkey')
    op.drop_index(op.f('ix_post_comments_user_id'), table_name='post_comments')
    op.drop_column('post_comments', 'user_id')
    if not _is_sqlite():
        op.drop_constraint(None, 'book_comments', type_='foreignkey')
    try:
        op.drop_index(op.f('ix_book_comments_user_id'), table_name='book_comments')
    except Exception:
        pass
    try:
        op.drop_column('book_comments', 'user_id')
    except Exception:
        pass
