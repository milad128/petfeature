"""add_reading_list_items_table

Revision ID: 26fbca410424
Revises: 29be8a288138
Create Date: 2026-07-31 02:03:52.884386

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '26fbca410424'
down_revision: Union[str, None] = '29be8a288138'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'reading_list_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column(
            'added_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'book_id', name='uq_reading_list_user_book'),
    )
    op.create_index(op.f('ix_reading_list_items_book_id'), 'reading_list_items', ['book_id'], unique=False)
    op.create_index(op.f('ix_reading_list_items_user_id'), 'reading_list_items', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_reading_list_items_user_id'), table_name='reading_list_items')
    op.drop_index(op.f('ix_reading_list_items_book_id'), table_name='reading_list_items')
    op.drop_table('reading_list_items')
