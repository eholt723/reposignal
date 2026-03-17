---
title: RepoSignal
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

[![CI](https://github.com/eholt723/reposignal/actions/workflows/ci.yml/badge.svg)](https://github.com/eholt723/reposignal/actions/workflows/ci.yml)

# RepoSignal

AI-powered GitHub Issues analytics dashboard. Enter any public GitHub repository — RepoSignal fetches real issues via the GitHub REST API, classifies each one by type, priority, and sentiment using an LLM, persists results to PostgreSQL, and renders a live analytics dashboard. Select any open issue to stream an AI-drafted triage response word-by-word in real time.

## Architecture

```
┌──────────────────────────────┐
│       React Frontend         │
│  Vite · Tailwind · Recharts  │
└──────────────┬───────────────┘
               │  REST  /api/*
               │  SSE   /api/draft/{id}
               ▼
┌──────────────────────────────────────────┐
│            FastAPI Backend               │
│                                          │
│  POST /api/analyze  ─── fetch + classify │
│  GET  /api/dashboard/{id} ─── SQL aggs   │
│  GET  /api/repos    ─── run history      │
│  POST /api/draft/{id} ─── SSE stream     │
└────────┬─────────────────────┬───────────┘
         │                     │
         ▼                     ▼
┌─────────────────┐   ┌─────────────────────┐
│  GitHub REST    │   │     Groq LLM        │
│  API            │   │  llama-3.3-70b      │
│  (fetch issues) │   │  (classify + draft) │
└────────┬────────┘   └──────────┬──────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
           ┌──────────────────┐
           │   PostgreSQL     │
           │   Neon serverless│
           │   raw SQL + JOIN │
           └──────────────────┘
```

| Layer | Responsibility |
|---|---|
| React frontend | Repo input, preset buttons, run history, dashboard charts, issue table, SSE-streamed draft panel |
| FastAPI backend | Route definitions, request validation, orchestrates fetch → classify → persist pipeline |
| GitHub client | Fetches up to 50 issues per repo via REST API; normalizes fields, filters PRs |
| Classifier | Sends each issue to Groq LLM; parses type, priority, sentiment, summary; parallelized with concurrency cap |
| Database | psycopg2 raw SQL — persists runs, issues, classifications; powers all aggregation queries |
| Draft panel | Streams an AI triage response word-by-word to the frontend via SSE |
| Migrations | Alembic tracks schema versions; migrations applied manually before deploy |

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI 0.115.5, Uvicorn 0.32.1 |
| Frontend | React 18, Vite 6, Tailwind CSS 3, Recharts 2, React Router 6 |
| LLM | Groq API — `llama-3.3-70b-versatile` (classify + draft) |
| Database | PostgreSQL via Neon serverless — raw SQL with psycopg2 2.9.10 |
| Real-time | Server-Sent Events via sse-starlette 2.1.3 |
| Migrations | Alembic 1.14.1 with SQLAlchemy 2.0 engine |
| Hosting | Hugging Face Spaces — multi-stage Docker (Node 20 build → Python 3.12 serve) |

## Features

- Repo input with 5 preset repositories (fastapi/fastapi, microsoft/vscode, vercel/next.js, golang/go, home-assistant/core)
- LLM classification: bug / feature request / question / docs · low / medium / high priority · sentiment score — parallelized with a concurrency cap to stay within Groq rate limits
- Analytics dashboard powered by SQL: COUNT + GROUP BY, time-series grouping by week, JOIN across issues and classifications
- Filterable issue table by type and priority
- AI-drafted triage response streamed live via SSE for any open issue
- Repo history — previously analyzed repos saved to DB and re-loadable from the landing page

## Local Development

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env   # fill in your keys
cd backend && uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend proxies `/api` requests to `http://localhost:8000` during dev.

## Testing

```bash
# Install the package in editable mode (once, from repo root)
pip install -e .

# Unit tests (no API key or database needed — all external calls mocked)
pytest tests/unit/ -v

# Integration tests (requires GROQ_API_KEY and DATABASE_URL in .env)
pytest tests/integration/ -v
```

| Suite | File | What it covers |
|---|---|---|
| Unit | `test_classifier.py` | `_validate` logic, `classify_issue` with mocked Groq, JSON fallback, stream chunk filtering |
| Unit | `test_github_client.py` | `_normalize` field mapping, PR filtering, `fetch_issues` pagination + max_issues cap |
| Unit | `test_routes.py` | All 9 API routes via FastAPI TestClient — happy path, 400/404/502 error cases |
| Integration | `test_lifecycle.py` | Full analyze → dashboard → issues → draft lifecycle against real Groq + PostgreSQL |

## Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key |
| `DATABASE_URL` | PostgreSQL connection string (e.g. Neon serverless) |
| `GITHUB_TOKEN` | Optional — increases GitHub API rate limit from 60 to 5000 req/hr |

## Project Structure

```
reposignal/
├── backend/
│   ├── main.py              # FastAPI app and all route definitions
│   ├── github_client.py     # GitHub REST API fetch, normalize, PR filter
│   ├── classifier.py        # Groq LLM classification pipeline (parallelized)
│   ├── database.py          # psycopg2 connection, SQL query functions
│   ├── models.py            # Pydantic request/response schemas
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.jsx                      # Router, layout, nav
│       └── components/
│           ├── RepoInput.jsx            # Repo input + preset buttons + run history
│           ├── Dashboard.jsx            # Main analytics view
│           ├── Charts/
│           │   ├── IssueTypeChart.jsx   # Bar chart — volume by type
│           │   ├── PriorityChart.jsx    # Pie chart — priority distribution
│           │   ├── OpenClosedChart.jsx  # Open vs closed ratio
│           │   ├── TimeSeriesChart.jsx  # Issues over time (weekly)
│           │   └── TopLabelsChart.jsx   # Top labels by frequency
│           ├── IssueList.jsx            # Filterable issue table
│           ├── DraftPanel.jsx           # SSE-streamed triage response
│           └── About.jsx                # Employer-facing showcase page
├── migrations/
│   ├── env.py               # Alembic runtime config — reads DATABASE_URL from env
│   └── versions/
│       ├── 0001_initial_schema.py      # Baseline: analysis_runs, issues, classifications
│       └── 0002_add_repo_description.py  # Adds repo_description column
├── tests/
│   ├── unit/
│   │   ├── test_classifier.py      # _validate, classify_issue, stream (mocked Groq)
│   │   ├── test_github_client.py   # _normalize, fetch_issues (mocked httpx)
│   │   └── test_routes.py          # All 9 API routes via FastAPI TestClient
│   └── integration/
│       └── test_lifecycle.py       # Full analyze → dashboard → issues → draft lifecycle
├── alembic.ini              # Alembic config — URL injected at runtime, not hardcoded
├── pyproject.toml           # Project metadata + pytest config
├── Dockerfile               # Multi-stage: Node 20 Vite build → Python 3.12 serve
└── docker-compose.yml       # Local dev: app + postgres
```

## Migrations

Database schema is managed by [Alembic](https://alembic.sqlalchemy.org/). Migration files live in `migrations/versions/` and are committed to the repo.

**Apply all pending migrations** (run from the project root):

```bash
alembic upgrade head
```

**Create a new migration** after changing the schema:

```bash
alembic revision -m "describe the change"
```

Then write the SQL changes in the generated file's `upgrade()` / `downgrade()` functions using `op.execute()`. This project uses raw psycopg2 rather than SQLAlchemy ORM, so `--autogenerate` is not available — migrations must be written manually.

> Always review the generated migration file before running it against any database. Never run `alembic upgrade head` blindly against production.

## Deployment

Deployed to Hugging Face Spaces via Docker. Push to the `space` remote to deploy:

```bash
git remote add space https://huggingface.co/spaces/eholt723/RepoSignal
git push space main
```
