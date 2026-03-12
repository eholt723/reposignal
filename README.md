---
title: RepoSignal
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# RepoSignal

AI-powered GitHub Issues analytics dashboard. Enter any public GitHub repository — RepoSignal fetches real issues via the GitHub REST API, classifies each one by type, priority, and sentiment using an LLM, persists results to PostgreSQL, and renders a live analytics dashboard. Select any open issue to stream an AI-drafted triage response word-by-word in real time.

## Architecture

```
GitHub REST API → classify (Groq) → persist (PostgreSQL) → dashboard (SQL aggregations)
                                                          → draft response (SSE stream)
```

| Layer | Responsibility |
|---|---|
| GitHub client | Fetches up to 100 issues per repo (no auth required for public repos) |
| Classifier | Groq LLM assigns type, priority, sentiment, and one-line summary to each issue |
| Database | PostgreSQL stores issues + classifications; SQL queries power all dashboard metrics |
| Dashboard | SQL-aggregated charts: volume by type, priority distribution, open/closed ratio, time series, top labels |
| Draft panel | SSE-streamed AI triage response for any selected open issue |

## Tech Stack

- **Frontend** — React + Vite + Tailwind CSS + Recharts
- **Backend** — Python + FastAPI with SSE streaming
- **LLM** — Groq (`llama-3.1-8b-instant`)
- **Database** — PostgreSQL (Neon) with raw SQL aggregation queries
- **Deploy** — Hugging Face Spaces (Docker)

## Features

- Repo input with 5 preset repositories (fastapi/fastapi, microsoft/vscode, vercel/next.js, golang/go, home-assistant/core)
- LLM classification: bug / feature request / question / docs · low / medium / high priority · sentiment score
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
│   ├── main.py              # FastAPI app, route definitions
│   ├── github_client.py     # GitHub REST API fetching logic
│   ├── classifier.py        # Groq classification pipeline
│   ├── database.py          # PostgreSQL connection, schema, SQL query functions
│   └── models.py            # Pydantic schemas
├── frontend/
│   └── src/
│       ├── App.jsx
│       └── components/
│           ├── RepoInput.jsx        # Repo input + preset buttons + history
│           ├── Dashboard.jsx        # Main analytics view
│           ├── Charts/              # Individual Recharts components
│           ├── IssueList.jsx        # Filterable issue table
│           ├── DraftPanel.jsx       # SSE-streamed triage draft
│           └── About.jsx            # Employer-facing showcase page
├── tests/
│   ├── unit/
│   │   ├── test_classifier.py   # _validate, classify_issue, stream (mocked Groq)
│   │   ├── test_github_client.py  # _normalize, fetch_issues (mocked httpx)
│   │   └── test_routes.py       # All API routes via FastAPI TestClient
│   └── integration/
│       └── test_lifecycle.py    # Full lifecycle: analyze → dashboard → draft
├── pyproject.toml           # Project metadata + pytest config
├── Dockerfile               # Multi-stage: Vite build + FastAPI serve
└── docker-compose.yml       # Local dev: app + postgres
```

## Deployment

Deployed to Hugging Face Spaces via Docker. Push to the `space` remote to deploy:

```bash
git remote add space https://huggingface.co/spaces/eholt723/RepoSignal
git push space main
```
