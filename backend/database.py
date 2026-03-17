import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://reposignal:reposignal@localhost:5432/reposignal")


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    # Schema is managed by Alembic migrations.
    # Run `alembic upgrade head` from the project root before starting the app.
    pass


def create_run(repo: str) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO analysis_runs (repo) VALUES (%s) RETURNING id",
                (repo,)
            )
            run_id = cur.fetchone()[0]
        conn.commit()
    return run_id


def insert_issue(run_id: int, issue: dict) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO issues (run_id, github_id, number, title, body, state, labels, created_at, closed_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                run_id,
                issue["github_id"],
                issue["number"],
                issue["title"],
                issue.get("body"),
                issue["state"],
                issue.get("labels", []),
                issue["created_at"],
                issue.get("closed_at"),
            ))
            issue_id = cur.fetchone()[0]
        conn.commit()
    return issue_id


def insert_classification(issue_id: int, clf: dict):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO classifications (issue_id, issue_type, priority, sentiment, summary)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                issue_id,
                clf["issue_type"],
                clf["priority"],
                clf["sentiment"],
                clf["summary"],
            ))
        conn.commit()


def update_run_count(run_id: int, count: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE analysis_runs SET issue_count = %s WHERE id = %s",
                (count, run_id)
            )
        conn.commit()


def get_dashboard(run_id: int) -> Optional[dict]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Run metadata
            cur.execute(
                "SELECT id, repo, analyzed_at, issue_count FROM analysis_runs WHERE id = %s",
                (run_id,)
            )
            run = cur.fetchone()
            if not run:
                return None

            # Open / closed counts
            cur.execute("""
                SELECT state, COUNT(*) AS count
                FROM issues
                WHERE run_id = %s
                GROUP BY state
            """, (run_id,))
            state_rows = cur.fetchall()
            state_map = {r["state"]: r["count"] for r in state_rows}

            # By type
            cur.execute("""
                SELECT c.issue_type, COUNT(*) AS count
                FROM issues i
                JOIN classifications c ON c.issue_id = i.id
                WHERE i.run_id = %s
                GROUP BY c.issue_type
                ORDER BY count DESC
            """, (run_id,))
            by_type = [{"issue_type": r["issue_type"], "count": r["count"]} for r in cur.fetchall()]

            # By priority
            cur.execute("""
                SELECT c.priority, COUNT(*) AS count
                FROM issues i
                JOIN classifications c ON c.issue_id = i.id
                WHERE i.run_id = %s
                GROUP BY c.priority
                ORDER BY count DESC
            """, (run_id,))
            by_priority = [{"priority": r["priority"], "count": r["count"]} for r in cur.fetchall()]

            # Top labels (unnest array)
            cur.execute("""
                SELECT label, COUNT(*) AS count
                FROM issues i, UNNEST(i.labels) AS label
                WHERE i.run_id = %s
                GROUP BY label
                ORDER BY count DESC
                LIMIT 10
            """, (run_id,))
            top_labels = [{"label": r["label"], "count": r["count"]} for r in cur.fetchall()]

            # Issues over time (weekly)
            cur.execute("""
                SELECT TO_CHAR(DATE_TRUNC('week', created_at), 'YYYY-MM-DD') AS week,
                       COUNT(*) AS count
                FROM issues
                WHERE run_id = %s
                GROUP BY DATE_TRUNC('week', created_at)
                ORDER BY DATE_TRUNC('week', created_at)
            """, (run_id,))
            over_time = [{"week": r["week"], "count": r["count"]} for r in cur.fetchall()]

    return {
        "run_id": run["id"],
        "repo": run["repo"],
        "analyzed_at": run["analyzed_at"],
        "total_issues": run["issue_count"],
        "open_count": state_map.get("open", 0),
        "closed_count": state_map.get("closed", 0),
        "by_type": by_type,
        "by_priority": by_priority,
        "top_labels": top_labels,
        "issues_over_time": over_time,
    }


def get_repo_history() -> list[dict]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT id AS run_id, repo, analyzed_at, issue_count
                FROM analysis_runs
                ORDER BY analyzed_at DESC
                LIMIT 5
            """)
            return [dict(r) for r in cur.fetchall()]


def get_issues_for_run(run_id: int) -> list[dict]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT i.id, i.github_id, i.number, i.title, i.state, i.labels, i.created_at,
                       c.issue_type, c.priority, c.sentiment, c.summary
                FROM issues i
                LEFT JOIN classifications c ON c.issue_id = i.id
                WHERE i.run_id = %s
                ORDER BY i.number DESC
            """, (run_id,))
            return [dict(r) for r in cur.fetchall()]


def get_issue_by_id(issue_id: int) -> Optional[dict]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT i.id, i.github_id, i.number, i.title, i.body, i.state, i.labels, i.created_at,
                       c.issue_type, c.priority, c.sentiment, c.summary
                FROM issues i
                LEFT JOIN classifications c ON c.issue_id = i.id
                WHERE i.id = %s
            """, (issue_id,))
            row = cur.fetchone()
            return dict(row) if row else None
