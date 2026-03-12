from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AnalyzeRequest(BaseModel):
    repo: str  # e.g. "fastapi/fastapi"
    max_issues: int = 100


class Classification(BaseModel):
    issue_type: str       # bug | feature_request | question | docs | other
    priority: str         # low | medium | high
    sentiment: str        # positive | neutral | negative
    summary: str          # one-line summary


class IssueRecord(BaseModel):
    github_id: int
    number: int
    title: str
    body: Optional[str]
    state: str            # open | closed
    labels: list[str]
    created_at: datetime
    closed_at: Optional[datetime]
    classification: Optional[Classification] = None


class AnalyzeResponse(BaseModel):
    run_id: int
    repo: str
    issue_count: int


class TypeCount(BaseModel):
    issue_type: str
    count: int


class PriorityCount(BaseModel):
    priority: str
    count: int


class LabelCount(BaseModel):
    label: str
    count: int


class WeeklyCount(BaseModel):
    week: str
    count: int


class DashboardResponse(BaseModel):
    run_id: int
    repo: str
    analyzed_at: datetime
    total_issues: int
    open_count: int
    closed_count: int
    by_type: list[TypeCount]
    by_priority: list[PriorityCount]
    top_labels: list[LabelCount]
    issues_over_time: list[WeeklyCount]


class RepoHistoryItem(BaseModel):
    run_id: int
    repo: str
    analyzed_at: datetime
    issue_count: int


class IssueSummary(BaseModel):
    id: int
    github_id: int
    number: int
    title: str
    state: str
    issue_type: Optional[str]
    priority: Optional[str]
    sentiment: Optional[str]
    summary: Optional[str]
    labels: list[str]
    created_at: datetime
