---
title: RepoSignal
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# RepoSignal

AI-powered GitHub Issues analytics dashboard. Enter any public GitHub repository to fetch issues, classify them by type and priority using an LLM, and explore a live analytics dashboard with trend charts and AI-drafted triage responses.

## Stack

Python · FastAPI · Groq · GitHub REST API · PostgreSQL (Neon) · React · Vite · Tailwind CSS · Docker

## Features

- Fetch up to 100 issues from any public GitHub repo
- LLM classification: type, priority, sentiment, one-line summary
- Analytics dashboard: volume by type, priority distribution, open/closed ratio, time series, top labels
- AI-drafted triage response streamed live for any open issue
- Repo history — previously analyzed repos saved and re-loadable
