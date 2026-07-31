"""drop subscribers table — email newsletter removed from the product

The email newsletter was removed in July 2026. Telegram (@petfeature) is the
only subscription channel. This drops the `subscribers` table created in
4716ef14fd90; that migration is left untouched because it is already applied
in production.

Revision ID: b7c1d4e9a205
Revises: 26fbca410424
Create Date: 2026-07-31 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b7c1d4e9a205'
down_revision: Union[str, None] = '26fbca410424'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table('subscribers')


def downgrade() -> None:
    op.create_table(
        'subscribers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('email', sa.String(300), nullable=False),
        sa.Column(
            'subscribed_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
