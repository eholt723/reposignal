"""
Integration tests — require GROQ_API_KEY and DATABASE_URL in .env.
These tests hit real external services and validate the full lifecycle.

Run with:
    pytest tests/integration/ -v
"""
import os
import pytest
from fastapi.testclient import TestClient
from dotenv import load_dotenv

load_dotenv()

# Skip entire module if required env vars are absent
pytestmark = pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY") or not os.getenv("DATABASE_URL"),
    reason="GROQ_API_KEY and DATABASE_URL required for integration tests",
)


@pytest.fixture(scope="module")
def api():
    from backend.main import app
    return TestClient(app)


# ---------------------------------------------------------------------------
# Full analyze → dashboard → issues → draft lifecycle
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def run_result(api):
    """
    Analyze a small real repo once and share the result across tests in
    this module so we don't make redundant API calls.
    """
    resp = api.post("/api/analyze", json={"repo": "fastapi/fastapi", "max_issues": 5})
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_analyze_returns_valid_shape(run_result):
    assert "run_id" in run_result
    assert run_result["repo"] == "fastapi/fastapi"
    assert run_result["issue_count"] > 0


def test_dashboard_returns_aggregations(api, run_result):
    run_id = run_result["run_id"]
    resp = api.get(f"/api/dashboard/{run_id}")
    assert resp.status_code == 200
    body = resp.json()

    assert body["run_id"] == run_id
    assert body["total_issues"] > 0
    assert isinstance(body["by_type"], list)
    assert isinstance(body["by_priority"], list)
    assert isinstance(body["issues_over_time"], list)

    # open + closed should sum to total
    assert body["open_count"] + body["closed_count"] == body["total_issues"]


def test_classifications_use_valid_schema(api, run_result):
    """Every classified issue must have schema-valid type/priority/sentiment."""
    run_id = run_result["run_id"]
    resp = api.get(f"/api/issues/{run_id}")
    assert resp.status_code == 200
    issues = resp.json()
    assert len(issues) > 0

    valid_types = {"bug", "feature_request", "question", "docs", "other"}
    valid_priorities = {"low", "medium", "high"}
    valid_sentiments = {"positive", "neutral", "negative"}

    for issue in issues:
        if issue["issue_type"] is not None:
            assert issue["issue_type"] in valid_types, f"bad type: {issue['issue_type']}"
        if issue["priority"] is not None:
            assert issue["priority"] in valid_priorities, f"bad priority: {issue['priority']}"
        if issue["sentiment"] is not None:
            assert issue["sentiment"] in valid_sentiments, f"bad sentiment: {issue['sentiment']}"


def test_dashboard_is_not_found_for_unknown_run(api):
    resp = api.get("/api/dashboard/999999")
    assert resp.status_code == 404


def test_repo_history_includes_analyzed_repo(api, run_result):
    resp = api.get("/api/repos")
    assert resp.status_code == 200
    repos = [r["repo"] for r in resp.json()]
    assert "fastapi/fastapi" in repos


def test_draft_streams_for_open_issue(api, run_result):
    """Find an open issue from the run and confirm SSE draft endpoint responds."""
    run_id = run_result["run_id"]
    issues = api.get(f"/api/issues/{run_id}").json()
    open_issues = [i for i in issues if i["state"] == "open"]

    if not open_issues:
        pytest.skip("No open issues returned for this run")

    issue_id = open_issues[0]["id"]
    with api.stream("POST", f"/api/draft/{issue_id}") as resp:
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]

        # Read at least one chunk to confirm streaming works
        raw = b""
        for chunk in resp.iter_bytes():
            raw += chunk
            if len(raw) > 20:
                break

        assert len(raw) > 0
