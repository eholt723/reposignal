"""
Unit tests for FastAPI routes — database and external API calls are mocked.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------

SAMPLE_ISSUE = {
    "github_id": 1001,
    "number": 7,
    "title": "App crashes on login",
    "body": "Steps: open app, click login, crash.",
    "state": "open",
    "labels": ["bug"],
    "created_at": "2024-03-01T00:00:00Z",
    "closed_at": None,
}

SAMPLE_CLASSIFICATION = {
    "issue_type": "bug",
    "priority": "high",
    "sentiment": "negative",
    "summary": "App crashes on login screen.",
}

SAMPLE_DASHBOARD = {
    "run_id": 1,
    "repo": "owner/repo",
    "analyzed_at": "2024-03-01T00:00:00+00:00",
    "total_issues": 5,
    "open_count": 3,
    "closed_count": 2,
    "by_type": [{"issue_type": "bug", "count": 3}],
    "by_priority": [{"priority": "high", "count": 2}],
    "top_labels": [{"label": "bug", "count": 3}],
    "issues_over_time": [{"week": "2024-03-04", "count": 5}],
}


# ---------------------------------------------------------------------------
# POST /api/analyze
# ---------------------------------------------------------------------------

@patch("backend.main.fetch_issues", return_value=[SAMPLE_ISSUE])
@patch("backend.main.classify_issue", return_value=SAMPLE_CLASSIFICATION)
@patch("backend.main.create_run", return_value=1)
@patch("backend.main.insert_issue", return_value=42)
@patch("backend.main.insert_classification")
@patch("backend.main.update_run_count")
def test_analyze_returns_run_id(
    mock_update, mock_insert_clf, mock_insert_issue,
    mock_create_run, mock_classify, mock_fetch
):
    resp = client.post("/api/analyze", json={"repo": "owner/repo"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["run_id"] == 1
    assert body["repo"] == "owner/repo"
    assert body["issue_count"] == 1


def test_analyze_rejects_bad_repo_format():
    resp = client.post("/api/analyze", json={"repo": "notavalidrepo"})
    assert resp.status_code == 400
    assert "owner/name" in resp.json()["detail"]


def test_analyze_rejects_empty_repo():
    resp = client.post("/api/analyze", json={"repo": "/"})
    assert resp.status_code == 400


@patch("backend.main.fetch_issues", side_effect=Exception("rate limited"))
def test_analyze_returns_502_on_github_error(mock_fetch):
    resp = client.post("/api/analyze", json={"repo": "owner/repo"})
    assert resp.status_code == 502
    assert "GitHub API error" in resp.json()["detail"]


@patch("backend.main.fetch_issues", return_value=[])
def test_analyze_returns_404_when_no_issues(mock_fetch):
    resp = client.post("/api/analyze", json={"repo": "owner/empty-repo"})
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/dashboard/{run_id}
# ---------------------------------------------------------------------------

@patch("backend.main.get_dashboard", return_value=SAMPLE_DASHBOARD)
def test_dashboard_returns_data(mock_get):
    resp = client.get("/api/dashboard/1")
    assert resp.status_code == 200
    body = resp.json()
    assert body["run_id"] == 1
    assert body["open_count"] == 3
    assert len(body["by_type"]) == 1


@patch("backend.main.get_dashboard", return_value=None)
def test_dashboard_404_on_missing_run(mock_get):
    resp = client.get("/api/dashboard/9999")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/repos
# ---------------------------------------------------------------------------

@patch("backend.main.get_repo_history", return_value=[
    {"run_id": 1, "repo": "owner/repo", "analyzed_at": "2024-03-01T00:00:00+00:00", "issue_count": 5}
])
def test_repos_returns_history(mock_get):
    resp = client.get("/api/repos")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["repo"] == "owner/repo"


@patch("backend.main.get_repo_history", return_value=[])
def test_repos_returns_empty_list(mock_get):
    resp = client.get("/api/repos")
    assert resp.status_code == 200
    assert resp.json() == []


# ---------------------------------------------------------------------------
# GET /api/issues/{run_id}
# ---------------------------------------------------------------------------

@patch("backend.main.get_issues_for_run", return_value=[
    {
        "id": 42, "github_id": 1001, "number": 7, "title": "App crashes",
        "state": "open", "issue_type": "bug", "priority": "high",
        "sentiment": "negative", "summary": "Crash on login.", "labels": ["bug"],
        "created_at": "2024-03-01T00:00:00+00:00",
    }
])
def test_issues_returns_list(mock_get):
    resp = client.get("/api/issues/1")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["issue_type"] == "bug"


# ---------------------------------------------------------------------------
# POST /api/draft/{issue_id}
# ---------------------------------------------------------------------------

@patch("backend.main.get_issue_by_id", return_value=None)
def test_draft_404_on_missing_issue(mock_get):
    resp = client.post("/api/draft/9999")
    assert resp.status_code == 404


@patch("backend.main.get_issue_by_id", return_value={
    "id": 42, "title": "App crashes", "body": "It crashes.",
    "state": "open", "issue_type": "bug", "priority": "high",
})
@patch("backend.main.stream_draft_response", return_value=iter(["Thank you", " for filing", " this issue."]))
def test_draft_streams_sse(mock_stream, mock_get):
    with client.stream("POST", "/api/draft/42") as resp:
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]
