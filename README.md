# Idea Tracker

**Local-first, open-source idea capture → execution system.**

Capture ideas, structure them with AI, track status through the pipeline (Idea → Research → Validate → Build → Paused/Killed → Done), and never let a good idea slip away.

## Features

- **Capture** — add ideas with title + description
- **Structure** — AI converts vague ideas into problem + opportunity statements
- **Pipeline** — track status: Idea → Research → Validate → Build → Paused/Killed → Done
- **Filter** — browse by status
- **Local-first** — SQLite, runs entirely offline
- **Open-source** — Apache-2.0

## Quick Start

Using [`uv`](https://github.com/astral-sh/uv):

```bash
# Install dependencies and sync environment
uv sync

# Run the local server
uv run uvicorn main:app --reload
```

Open [http://localhost:8000](http://localhost:8000).

## Stack

FastAPI + SQLite + SQLAlchemy + Jinja2 — no external AI APIs needed (heuristic structuring built-in; swap in Laya/Jev later).
