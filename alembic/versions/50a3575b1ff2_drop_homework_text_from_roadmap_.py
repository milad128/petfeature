"""drop homework_text from roadmap_resources

Revision ID: 50a3575b1ff2
Revises: c2bd9dc6e5a8
Create Date: 2026-08-04 16:21:00.281870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50a3575b1ff2'
down_revision: Union[str, None] = 'c2bd9dc6e5a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('roadmap_resources', 'homework_text')


def downgrade() -> None:
    op.add_column('roadmap_resources', sa.Column('homework_text', sa.TEXT(), nullable=True))
