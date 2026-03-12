import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a software triage assistant. Given a GitHub issue title and body, classify it and return a JSON object with exactly these fields:

- issue_type: one of "bug", "feature_request", "question", "docs", "other"
- priority: one of "low", "medium", "high"
- sentiment: one of "positive", "neutral", "negative"
- summary: a single sentence (max 20 words) describing the issue

Return only valid JSON. No markdown, no explanation."""


def classify_issue(title: str, body: str) -> dict:
    """
    Classify a single GitHub issue using Groq.
    Returns a dict with issue_type, priority, sentiment, summary.
    """
    truncated_body = (body or "")[:1000]
    user_content = f"Title: {title}\n\nBody: {truncated_body}"

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.1,
        max_tokens=200,
    )

    raw = response.choices[0].message.content.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback if model returns malformed JSON
        result = {
            "issue_type": "other",
            "priority": "low",
            "sentiment": "neutral",
            "summary": title[:100],
        }

    return _validate(result)


def _validate(result: dict) -> dict:
    valid_types = {"bug", "feature_request", "question", "docs", "other"}
    valid_priorities = {"low", "medium", "high"}
    valid_sentiments = {"positive", "neutral", "negative"}

    return {
        "issue_type": result.get("issue_type", "other") if result.get("issue_type") in valid_types else "other",
        "priority": result.get("priority", "low") if result.get("priority") in valid_priorities else "low",
        "sentiment": result.get("sentiment", "neutral") if result.get("sentiment") in valid_sentiments else "neutral",
        "summary": str(result.get("summary", ""))[:200],
    }


def stream_draft_response(issue_title: str, issue_body: str, issue_type: str, priority: str):
    """
    Generator that streams an AI triage response for a given issue.
    Yields text chunks.
    """
    truncated_body = (issue_body or "")[:1500]
    prompt = f"""You are a helpful open-source maintainer. Write a concise, friendly triage response to this GitHub issue.

Issue type: {issue_type}
Priority: {priority}
Title: {issue_title}

Body:
{truncated_body}

Write a response that:
- Acknowledges the issue
- Asks any clarifying questions if it's a bug
- Sets expectations for timeline based on priority
- Is warm and professional
- Is 3-5 sentences max"""

    stream = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300,
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
