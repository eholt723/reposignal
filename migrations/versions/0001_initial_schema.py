"""initial schema

Revision ID: 0001
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS analysis_runs (
            id          SERIAL PRIMARY KEY,
            repo        TEXT NOT NULL,
            analyzed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            issue_count INT NOT NULL DEFAULT 0
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS issues (
            id          SERIAL PRIMARY KEY,
            run_id      INT NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
            github_id   BIGINT NOT NULL,
            number      INT NOT NULL,
            title       TEXT NOT NULL,
            body        TEXT,
            state       TEXT NOT NULL,
            labels      TEXT[],
            created_at  TIMESTAMPTZ NOT NULL,
            closed_at   TIMESTAMPTZ
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS classifications (
            id          SERIAL PRIMARY KEY,
            issue_id    INT NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
            issue_type  TEXT NOT NULL,
            priority    TEXT NOT NULL,
            sentiment   TEXT NOT NULL,
            summary     TEXT NOT NULL
        )
    """)

    op.execute("CREATE INDEX IF NOT EXISTS idx_issues_run_id ON issues(run_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_classifications_issue_id ON classifications(issue_id)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_classifications_issue_id")
    op.execute("DROP INDEX IF EXISTS idx_issues_run_id")
    op.execute("DROP TABLE IF EXISTS classifications")
    op.execute("DROP TABLE IF EXISTS issues")
    op.execute("DROP TABLE IF EXISTS analysis_runs")
