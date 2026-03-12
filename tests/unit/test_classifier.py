"""
Unit tests for classifier.py — all Groq calls are mocked.
"""
import json
import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# _validate
# ---------------------------------------------------------------------------

from backend.classifier import _validate


def test_validate_passes_valid_input():
    result = _validate({
        "issue_type": "bug",
        "priority": "high",
        "sentiment": "negative",
        "summary": "App crashes on startup",
    })
    assert result == {
        "issue_type": "bug",
        "priority": "high",
        "sentiment": "negative",
        "summary": "App crashes on startup",
    }


def test_validate_falls_back_on_invalid_type():
    result = _validate({"issue_type": "nonsense", "priority": "low", "sentiment": "neutral", "summary": "x"})
    assert result["issue_type"] == "other"


def test_validate_falls_back_on_invalid_priority():
    result = _validate({"issue_type": "bug", "priority": "critical", "sentiment": "neutral", "summary": "x"})
    assert result["priority"] == "low"


def test_validate_falls_back_on_invalid_sentiment():
    result = _validate({"issue_type": "bug", "priority": "low", "sentiment": "angry", "summary": "x"})
    assert result["sentiment"] == "neutral"


def test_validate_truncates_long_summary():
    result = _validate({
        "issue_type": "docs",
        "priority": "low",
        "sentiment": "neutral",
        "summary": "x" * 300,
    })
    assert len(result["summary"]) <= 200


def test_validate_handles_missing_fields():
    result = _validate({})
    assert result["issue_type"] == "other"
    assert result["priority"] == "low"
    assert result["sentiment"] == "neutral"
    assert result["summary"] == ""


# ---------------------------------------------------------------------------
# classify_issue
# ---------------------------------------------------------------------------

from backend.classifier import classify_issue


def _make_groq_response(content: str):
    """Build a minimal mock that looks like a Groq chat completion response."""
    choice = MagicMock()
    choice.message.content = content
    resp = MagicMock()
    resp.choices = [choice]
    return resp


@patch("backend.classifier.client")
def test_classify_issue_returns_valid_dict(mock_client):
    payload = {
        "issue_type": "feature_request",
        "priority": "medium",
        "sentiment": "positive",
        "summary": "User requests dark mode support",
    }
    mock_client.chat.completions.create.return_value = _make_groq_response(json.dumps(payload))

    result = classify_issue("Add dark mode", "Please add a dark mode option.")

    assert result["issue_type"] == "feature_request"
    assert result["priority"] == "medium"
    assert result["sentiment"] == "positive"
    assert "dark mode" in result["summary"].lower()


@patch("backend.classifier.client")
def test_classify_issue_falls_back_on_bad_json(mock_client):
    mock_client.chat.completions.create.return_value = _make_groq_response("not valid json at all")

    result = classify_issue("Some title", "Some body")

    # Should return fallback defaults, not raise
    assert result["issue_type"] == "other"
    assert result["priority"] == "low"
    assert result["sentiment"] == "neutral"


@patch("backend.classifier.client")
def test_classify_issue_truncates_body(mock_client):
    """Body longer than 1000 chars should be truncated before sending to Groq."""
    payload = {"issue_type": "bug", "priority": "high", "sentiment": "negative", "summary": "long body test"}
    mock_client.chat.completions.create.return_value = _make_groq_response(json.dumps(payload))

    long_body = "a" * 5000
    classify_issue("Title", long_body)

    call_args = mock_client.chat.completions.create.call_args
    user_message = call_args.kwargs["messages"][1]["content"]
    assert len(user_message) < 5000 + 100  # title + truncated body, well under 5100


# ---------------------------------------------------------------------------
# stream_draft_response
# ---------------------------------------------------------------------------

from backend.classifier import stream_draft_response


@patch("backend.classifier.client")
def test_stream_draft_response_yields_chunks(mock_client):
    chunks = ["Hello", " there", ", thanks", " for filing", " this issue."]

    def make_chunk(text):
        c = MagicMock()
        c.choices[0].delta.content = text
        return c

    mock_client.chat.completions.create.return_value = [make_chunk(t) for t in chunks]

    result = list(stream_draft_response(
        issue_title="App crashes",
        issue_body="Steps to reproduce: ...",
        issue_type="bug",
        priority="high",
    ))

    assert result == chunks


@patch("backend.classifier.client")
def test_stream_draft_response_skips_none_deltas(mock_client):
    def make_chunk(text):
        c = MagicMock()
        c.choices[0].delta.content = text
        return c

    mock_client.chat.completions.create.return_value = [
        make_chunk("Hello"),
        make_chunk(None),
        make_chunk(" world"),
    ]

    result = list(stream_draft_response("Title", "Body", "question", "low"))
    assert None not in result
    assert result == ["Hello", " world"]
