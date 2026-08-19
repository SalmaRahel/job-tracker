"""make job_description not nullable

Revision ID: 622c6479a867
Revises: 7a2d3606ac69
Create Date: 2026-08-19 20:05:27.046955

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '622c6479a867'
down_revision: Union[str, Sequence[str], None] = '7a2d3606ac69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('job', 'job_description',
               existing_type=sa.TEXT(),
               nullable=False)

def downgrade() -> None:
    op.alter_column('job', 'job_description',
               existing_type=sa.TEXT(),
               nullable=True)
