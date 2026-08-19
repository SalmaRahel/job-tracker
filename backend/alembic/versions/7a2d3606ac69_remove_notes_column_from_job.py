"""remove notes column from job

Revision ID: 7a2d3606ac69
Revises: c6f16e815020
Create Date: 2026-08-19 18:47:08.324811

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a2d3606ac69'
down_revision: Union[str, Sequence[str], None] = 'c6f16e815020'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('job', 'notes')

def downgrade() -> None:
    op.add_column('job', sa.Column('notes', sa.TEXT(), nullable=True))
