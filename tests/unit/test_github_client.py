"""
Unit tests for github_client.py — all HTTP calls are mocked.
"""
import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# _normalize
# ---------------------------------------------------------------------------

from backend.github_client import _normalize


SAMPLE_ITEM = {
    "id": 123456,
    "number": 42,
    "title": "Fix null pointer in auth module",
    "body": "Steps to reproduce: ...",
    "state": "open",
    "labels": [{"name": "bug"}, {"name": "good first issue"}],
    "created_at": "2024-01-15T10:00:00Z",
    "closed_at": None,
}


def test_normalize_extracts_all_fields():
    result = _normalize(SAMPLE_ITEM)
    assert result["github_id"] == 123456
    assert result["number"] == 42
    assert result["title"] == "Fix null pointer in auth module"
    assert result["body"] == "Steps to reproduce: ..."
    assert result["state"] == "open"
    assert result["labels"] == ["bug", "good first issue"]
    assert result["created_at"] == "2024-01-15T10:00:00Z"
    assert result["closed_at"] is None


def test_normalize_handles_missing_body():
    item = {**SAMPLE_ITEM, "body": None}
    result = _normalize(item)
    assert result["body"] == ""


def test_normalize_handles_empty_labels():
    item = {**SAMPLE_ITEM, "labels": []}
    result = _normalize(item)
    assert result["labels"] == []


def test_normalize_closed_issue():
    item = {**SAMPLE_ITEM, "state": "closed", "closed_at": "2024-02-01T12:00:00Z"}
    result = _normalize(item)
    assert result["state"] == "closed"
    assert result["closed_at"] == "2024-02-01T12:00:00Z"


# ---------------------------------------------------------------------------
# fetch_issues
# ---------------------------------------------------------------------------

from backend.github_client import fetch_issues


def _make_mock_response(items: list, status_code: int = 200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = items
    resp.raise_for_status = MagicMock()
    return resp


def _make_issue_item(n: int, is_pr: bool = False) -> dict:
    item = {
        "id": 1000 + n,
        "number": n,
        "title": f"Issue {n}",
        "body": f"Body {n}",
        "state": "open",
        "labels": [],
        "created_at": "2024-01-01T00:00:00Z",
        "closed_at": None,
    }
    if is_pr:
        item["pull_request"] = {"url": "https://github.com/..."}
    return item


@patch("backend.github_client.httpx.Client")
def test_fetch_issues_returns_normalized_issues(mock_client_cls):
    items = [_make_issue_item(i) for i in range(1, 6)]
    mock_resp = _make_mock_response(items)
    # Second call returns empty list to stop pagination
    mock_client = MagicMock()
    mock_client.get.side_effect = [mock_resp, _make_mock_response([])]
    mock_client_cls.return_value.__enter__.return_value = mock_client

    results = fetch_issues("owner/repo", max_issues=10)

    assert len(results) == 5
    assert results[0]["number"] == 1
    assert "github_id" in results[0]


@patch("backend.github_client.httpx.Client")
def test_fetch_issues_filters_pull_requests(mock_client_cls):
    items = [
        _make_issue_item(1),
        _make_issue_item(2, is_pr=True),
        _make_issue_item(3),
    ]
    mock_client = MagicMock()
    mock_client.get.side_effect = [_make_mock_response(items), _make_mock_response([])]
    mock_client_cls.return_value.__enter__.return_value = mock_client

    results = fetch_issues("owner/repo", max_issues=10)

    assert len(results) == 2
    numbers = {r["number"] for r in results}
    assert 2 not in numbers


@patch("backend.github_client.httpx.Client")
def test_fetch_issues_respects_max_issues(mock_client_cls):
    # Return 10 issues but cap at 3
    items = [_make_issue_item(i) for i in range(1, 11)]
    mock_client = MagicMock()
    mock_client.get.return_value = _make_mock_response(items)
    mock_client_cls.return_value.__enter__.return_value = mock_client

    results = fetch_issues("owner/repo", max_issues=3)

    assert len(results) == 3


@patch("backend.github_client.httpx.Client")
def test_fetch_issues_stops_on_empty_page(mock_client_cls):
    mock_client = MagicMock()
    mock_client.get.return_value = _make_mock_response([])
    mock_client_cls.return_value.__enter__.return_value = mock_client

    results = fetch_issues("owner/repo", max_issues=100)

    assert results == []
