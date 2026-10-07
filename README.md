# Idea Tracker

**An open-source, local-first system for turning vague ideas into structured, validated execution.**

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)

---

## What is this?

Idea Tracker is a local-first application designed to help ambitious developers, founders, and creators systematically turn ideas into outcomes.

Most idea notebooks become graveyards of half-baked thoughts. Idea Tracker changes the core loop:

```text
CAPTURE → STRUCTURE → UNDERSTAND → VALIDATE → DECIDE → EXECUTE → REVIEW → LEARN
```

Instead of another passive note-taking app, Idea Tracker asks the central question:

> **"What should I do with this idea next?"**

---

## Why does it exist?

1. **Ideas need evidence, not hype** — AI shouldn't make decisions for you; it should extract risks, assumptions, and suggest smallest next actions grounded in evidence.
2. **Local-first privacy** — Your product ideas, strategic notes, and validation data belong on your machine in standard formats (SQLite/JSON/Markdown).
3. **Execution-focused** — A great idea without explicit decisions and milestones is just a distraction.

---

## Core Philosophy

- **Human makes the final decision** — AI assists reasoning and structures raw input, but never silently alters state or makes commitments.
- **Traceability** — Every assessment, risk score, or decision traces back to explicit evidence or is marked `UNVERIFIED`.
- **Modular Monolith** — Simple single-process application with clean layer separation. No microservices, no mandatory cloud dependencies.
- **Replaceable AI Providers** — Works out-of-the-box with local LLMs (Ollama) or external APIs (OpenAI, Anthropic) via a provider abstraction.

---

## Architecture

**Note:** The codebase includes both FastAPI (backend) and Streamlit (frontend) implementations. The README describes the original FastAPI+HTMX design; the `idea-tracker/pages/` directory and `app.py` provide a Streamlit UI layer.

Idea Tracker follows a clean **Modular Monolith** architecture:

```text
┌─────────────────────────────────────────┐
│        Web Layer (FastAPI + HTMX)       │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│      Application Layer (Use Cases)      │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│          Domain Layer (Entities)        │
└────────────────────▲────────────────────┘
                     │
┌────────────────────┴────────────────────┐
│     Infrastructure Layer (Adapters)     │
│   (SQLite / Ollama / OpenAI / Anthropic)│
└─────────────────────────────────────────┘
```

For detailed architecture diagrams and design records, see [`docs/architecture/`](docs/architecture/) and [`docs/decisions/`](docs/decisions/).

---

## Features

- ⚡ **Quick Capture** — Instantly capture ideas in seconds without mandatory structured fields.
- 🤖 **AI Structuring** — Automatically convert raw notes into problem statements, target user profiles, opportunities, assumptions, and risks.
- 📋 **Lifecycle Tracking** — Track ideas across clear states (`INBOX` → `STRUCTURED` → `EXPLORING` → `VALIDATING` → `COMMITTED` → `BUILDING` → `LAUNCHED` / `PAUSED` / `KILLED`).
- 📜 **Append-only Activity Log** — Immutable history of every state change, AI run, task completion, and decision.
- 🎯 **Execution Planning** — Break down ideas into milestones and prioritized, actionable tasks.
- 🔍 **Local Search** — SQLite FTS5 full-text search across titles, descriptions, notes, and tags.
- 🔄 **Review Engine** — Detect forgotten, stale, or blocked ideas and guide weekly review workflows.

---

## Quick Start

### Prerequisites

- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv) (recommended Python package manager)

### 1. Clone & Setup

```bash
git clone https://github.com/GaneshPatil-Ai/littleMore.git
cd littleMore/idea-tracker

# Install dependencies and setup virtual environment
uv sync --extra dev
```

### 2. Configure Environment

```bash
cp .env.example .env
```

*(Defaults work out-of-the-box for local SQLite and Ollama).*

### 3. Run Application

```bash
make dev
# or
uv run uvicorn idea_tracker.main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. Verification endpoint: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

---

## 🚀 Docker Deployment

### Local Development
```bash
docker compose up -d
```

This starts both the app and Ollama service. Access at `http://localhost:8000`.

### Production
```bash
docker compose up -d
```

Use a production-ready `.env` with your preferred LLM provider.

---

## 📚 Documentation

- [Architecture Overview](docs/architecture/)
- [Design Decisions](docs/decisions/)
- [API Reference](http://localhost:8000/docs)

---

## 🎯 Features

- **Quick Capture**: Instant idea creation
- **AI Structuring**: Auto-convert raw notes to structured format
- **Lifecycle Tracking**: 10+ states from INBOX to LAUNCHED
- **Execution Planning**: Milestones and prioritized tasks
- **Research Management**: Evidence and questions with citations
- **Search Intelligence**: Keyword, full-text, tag, and status search
- **Decision Tracking**: Explicit outcomes with rationale
- **Local-First**: All data stored on your machine
- **Privacy-First**: No external data dependencies

---

## 🏷️ Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

---

## 📜 License

Apache-2.0 License - see [LICENSE](LICENSE) file for details.
---

## Local AI Setup (Ollama)

To run fully offline with zero API cost:

1. Install [Ollama](https://ollama.ai/)
2. Pull a local model:
   ```bash
   ollama pull llama3.2
   ```
3. Set your `.env`:
   ```ini
   LLM_PROVIDER=ollama
   LLM_MODEL=llama3.2
   OLLAMA_BASE_URL=http://localhost:11434
   ```

---

## Docker Setup

Run using Docker Compose:

```bash
docker compose up -d
```

---

## Development & Testing

We enforce strict quality controls with `pytest`, `ruff`, and `mypy`.

```bash
# Run test suite
make test

# Run linter & type checker
make lint

# Run all checks (lint + test)
make check
```

---

## Roadmap

- [x] **Phase 1: Foundation** — Modular monolith architecture, configuration, logging, database, health check, test suite.
- [x] **Phase 2: Idea Core** — Domain entities, lifecycle state machine, activity event log, tags, notes, HTMX UI.
- [x] **Phase 3: Execution Engine** — Milestones, prioritized tasks, execution tracking.
- [x] **Phase 4: AI Core** — LLM provider abstraction (Ollama/OpenAI/Anthropic), structuring & next-action services.
- [x] **Phase 5: Reviews & Decisions** — Stale idea detection, explicit decision tracking, weekly review workflow.
- [x] **Phase 6: Research & Evidence** — Research questions, evidence links, source citations.
- [x] **Phase 7: Search Intelligence** — Keyword, full-text, tag, and status search capabilities.
- [x] **Phase 8: Open Source Release** — Docker image, export functionality, complete documentation release.

---

## Contributing

Contributions are welcome! Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) for details on our code of conduct and development process.

---

## License

This project is licensed under the Apache-2.0 License - see the [`LICENSE`](LICENSE) file for details.
