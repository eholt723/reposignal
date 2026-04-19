import os
import httpx
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")


def _headers() -> dict:
    h = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h


def fetch_issues(repo: str, max_issues: int = 100) -> list[dict]:
    """
    Fetch up to max_issues issues (open + closed) from a public GitHub repo.
    Returns a list of normalized issue dicts.
    """
    issues = []
    per_page = min(max_issues, 100)
    page = 1

    with httpx.Client(headers=_headers(), timeout=30, follow_redirects=True) as client:
        while len(issues) < max_issues:
            resp = client.get(
                f"{GITHUB_API}/repos/{repo}/issues",
                params={
                    "state": "all",
                    "per_page": per_page,
                    "page": page,
                    "sort": "created",
                    "direction": "desc",
                },
            )
            resp.raise_for_status()
            batch = resp.json()

            if not batch:
                break

            for item in batch:
                # Skip pull requests (GitHub includes them in /issues)
                if "pull_request" in item:
                    continue
                issues.append(_normalize(item))
                if len(issues) >= max_issues:
                    break

            if len(batch) < per_page:
                break

            page += 1

    return issues


def _normalize(item: dict) -> dict:
    return {
        "github_id": item["id"],
        "number": item["number"],
        "title": item["title"],
        "body": item.get("body") or "",
        "state": item["state"],
        "labels": [label["name"] for label in item.get("labels", [])],
        "created_at": item["created_at"],
        "closed_at": item.get("closed_at"),
    }
