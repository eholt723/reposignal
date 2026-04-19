from fastmcp import FastMCP
from .database import get_repo_history, get_dashboard, get_issues_for_run

mcp = FastMCP("RepoSignal")


@mcp.tool()
def list_recent_runs() -> list[dict]:
    """Return the 5 most recently analyzed repositories with their run IDs, repo names, timestamps, and issue counts."""
    return get_repo_history()


@mcp.tool()
def get_run_dashboard(run_id: int) -> dict:
    """Return analytics for an analysis run: issue counts by type and priority, open/closed ratio, top labels, and weekly trend data."""
    result = get_dashboard(run_id)
    if result is None:
        return {"error": f"No run found with id {run_id}"}
    return result


@mcp.tool()
def get_run_issues(run_id: int) -> list[dict]:
    """Return all classified issues for a run, including AI-assigned type, priority, sentiment, and one-line summary for each issue."""
    return get_issues_for_run(run_id)
