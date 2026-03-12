import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse
import os

from .models import AnalyzeRequest, AnalyzeResponse, DashboardResponse, RepoHistoryItem, IssueSummary
from .database import (
    init_db, create_run, insert_issue, insert_classification,
    update_run_count, get_dashboard, get_repo_history,
    get_issues_for_run, get_issue_by_id,
)
from .github_client import fetch_issues
from .classifier import classify_issue, stream_draft_response


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="RepoSignal", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    # Validate repo format
    parts = req.repo.strip().split("/")
    if len(parts) != 2 or not all(parts):
        raise HTTPException(status_code=400, detail="repo must be in 'owner/name' format")

    # Fetch issues from GitHub
    try:
        issues = fetch_issues(req.repo, req.max_issues)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"GitHub API error: {str(e)}")

    if not issues:
        raise HTTPException(status_code=404, detail="No issues found for this repository")

    # Create analysis run and insert all issues first
    run_id = create_run(req.repo)
    issue_records = [(insert_issue(run_id, issue), issue) for issue in issues]

    # Classify concurrently, max 15 at a time to stay under Groq rate limits
    semaphore = asyncio.Semaphore(15)
    loop = asyncio.get_event_loop()

    async def classify_and_store(issue_id, issue):
        async with semaphore:
            try:
                clf = await loop.run_in_executor(
                    None, classify_issue, issue["title"], issue.get("body", "")
                )
                insert_classification(issue_id, clf)
            except Exception:
                pass

    await asyncio.gather(*[classify_and_store(iid, iss) for iid, iss in issue_records])

    update_run_count(run_id, len(issues))

    return AnalyzeResponse(run_id=run_id, repo=req.repo, issue_count=len(issues))


@app.get("/api/dashboard/{run_id}", response_model=DashboardResponse)
def dashboard(run_id: int):
    data = get_dashboard(run_id)
    if not data:
        raise HTTPException(status_code=404, detail="Run not found")
    return data


@app.get("/api/repos", response_model=list[RepoHistoryItem])
def repos():
    return get_repo_history()


@app.get("/api/issues/{run_id}", response_model=list[IssueSummary])
def issues(run_id: int):
    return get_issues_for_run(run_id)


@app.post("/api/draft/{issue_id}")
async def draft(issue_id: int):
    issue = get_issue_by_id(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    async def event_generator():
        loop = asyncio.get_event_loop()
        gen = stream_draft_response(
            issue_title=issue["title"],
            issue_body=issue.get("body") or "",
            issue_type=issue.get("issue_type") or "other",
            priority=issue.get("priority") or "medium",
        )
        for chunk in gen:
            yield {"data": json.dumps({"chunk": chunk})}
        yield {"data": json.dumps({"done": True})}

    return EventSourceResponse(event_generator())


# Serve React frontend in production (when dist/ exists)
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
