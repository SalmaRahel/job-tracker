"""add search_vector to job

Revision ID: c6f16e815020
Revises: c26bc76e9d36
Create Date: 2026-08-19 17:51:23.079510

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TSVECTOR


# revision identifiers, used by Alembic.
revision: str = 'c6f16e815020'
down_revision: Union[str, Sequence[str], None] = 'c26bc76e9d36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('job', sa.Column('job_description', sa.Text()))
    op.execute('''ALTER TABLE job ADD COLUMN search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce(company_name, '') || ' ' || coalesce(position, '') || ' ' || coalesce(job_description, ''))) STORED''')
    op.execute('CREATE INDEX idx_search_vector ON job USING GIN (search_vector)')

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_search_vector', table_name='job')
    op.drop_column('job', 'search_vector')
    op.drop_column('job', 'job_description')


