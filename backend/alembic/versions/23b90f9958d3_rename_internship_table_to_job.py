"""rename internship table to job

Revision ID: 23b90f9958d3
Revises: 58cd0288962c
Create Date: 2026-08-05 22:28:23.154636

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23b90f9958d3'
down_revision: Union[str, Sequence[str], None] = '58cd0288962c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table('internship', 'job')
    op.execute('ALTER TABLE job RENAME CONSTRAINT internship_pkey TO job_pkey')
    op.execute('ALTER TABLE job RENAME CONSTRAINT internship_user_id_fkey TO job_user_id_fkey')
    op.execute('ALTER SEQUENCE internship_id_seq RENAME TO job_id_seq')


def downgrade() -> None:
    """Downgrade schema."""
    op.rename_table('job', 'internship')
    op.execute('ALTER TABLE internship RENAME CONSTRAINT job_pkey TO internship_pkey')
    op.execute('ALTER TABLE internship RENAME CONSTRAINT job_user_id_fkey TO internship_user_id_fkey')
    op.execute('ALTER SEQUENCE job_id_seq RENAME TO internship_id_seq')
