"""add repo_description to analysis_runs

Revision ID: 0002
Revises: 0001
Create Date: 2025-01-02 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE analysis_runs
        ADD COLUMN IF NOT EXISTS repo_description TEXT
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE analysis_runs
        DROP COLUMN IF EXISTS repo_description
    """)
