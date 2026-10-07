# Architecture Overview

## Philosophy

Idea Tracker is a **modular monolith** — a single deployable unit with clear internal module boundaries. This gives us the simplicity of a monolith (one process, one database, simple deployment) with the organizational benefits of well-separated concerns.

We explicitly avoid microservices. The problem domain is cohesive, the user count is small (local-first), and network boundaries between modules would add latency and complexity with no benefit.

## Core Product Loop

```
CAPTURE → STRUCTURE → UNDERSTAND → VALIDATE → DECIDE → EXECUTE → REVIEW → LEARN
    ↑                                                                          │
    └──────────────────────────────────────────────────────────────────────────┘
```

The central question the application answers: **"What should I do with this idea next?"**

The differentiating flow: **Idea → Evidence → Decision → Execution → Outcome**

## Dependency Direction

```
┌─────────────────────────┐
│    Web / API Layer      │  FastAPI routes, Streamlit frontend + FastAPI backend
│    (Presentation)       │
└────────────┬────────────┘
             │ depends on
             ▼
┌─────────────────────────┐
│   Application Layer     │  Use cases, services, orchestration
│   (Use Cases)           │
└────────────┬────────────┘
             │ depends on
             ▼
┌─────────────────────────┐
│     Domain Layer        │  Entities, value objects, domain rules,
│     (Core)              │  repository interfaces, service interfaces
└─────────────────────────┘
             ▲
             │ implements interfaces from
┌─────────────────────────┐
│  Infrastructure Layer   │  SQLAlchemy repos, LLM providers,
│  (Adapters)             │  search backends, schedulers
└─────────────────────────┘
```

**Key rule:** The domain layer has zero dependencies on frameworks, databases, or external services. It defines interfaces (protocols) that infrastructure implements.

## Module Structure

```
src/idea_tracker/
├── domain/              # Pure domain: entities, value objects, interfaces
│   ├── ideas/
│   ├── execution/
│   ├── research/
│   ├── validation/
│   ├── decisions/
│   └── reviews/
├── application/         # Use cases and service orchestration
│   ├── ideas/
│   ├── execution/
│   ├── ai/
│   ├── research/
│   ├── validation/
│   ├── decisions/
│   ├── reviews/
│   └── search/
├── infrastructure/      # Adapters: DB, LLM, search, scheduling
│   ├── database/
│   ├── llm/
│   ├── search/
│   └── scheduler/
├── web/                 # FastAPI routes, templates, static files
│   ├── routes/
│   ├── templates/
│   └── static/
├── config.py            # Environment-based configuration
└── main.py              # Application entry point
```

### Core Modules

| Module | Responsibility |
|--------|---------------|
| **ideas** | Idea lifecycle: capture, structure, status transitions, tags, notes |
| **execution** | Milestones, tasks, priorities, due dates |
| **research** | Research runs, questions, findings, evidence, sources |
| **validation** | Validation categories, scores, confidence, evidence linkage |
| **decisions** | Explicit decisions (build/pause/kill) with reasoning and evidence |
| **reviews** | Periodic reviews, stale/forgotten detection, weekly review workflow |
| **ai** | LLM provider abstraction, AI workflows (structuring, planning) |
| **search** | Search abstraction (FTS5 now, embeddings later) |
| **notifications** | Future: reminders, alerts (deferred beyond MVP) |

## Technology Stack

### Backend
- **Python 3.12+** — primary language
- **FastAPI** — HTTP framework
- **Pydantic v2** — validation and serialization
- **SQLAlchemy 2.x** — ORM and database access
- **Alembic** — database migrations
- **SQLite** — database (local-first)

### Frontend
- **Jinja2** — server-side templates
- **HTMX** — dynamic interactions without a JS framework
- **CSS** — styling (no CSS framework required)
- **Minimal vanilla JS** — only where HTMX cannot cover

### Development
- **uv** — package management and virtual environments
- **Ruff** — linting and formatting
- **pytest** — testing
- **mypy** — type checking
- **pre-commit** — git hooks
- **GitHub Actions** — CI/CD

### AI
- Provider abstraction with adapters for:
  - Ollama (local models)
  - OpenAI-compatible APIs
  - Anthropic-compatible APIs

### Search
- **Phase 1:** SQLite FTS5 + indexed queries
- **Future:** Local embeddings, pluggable vector index

### Deployment
- Local development via `uv run`
- Docker / Docker Compose

## Request Flow

A typical request follows this path:

```
Browser (Streamlit + API request)
    │
    ▼
FastAPI Route (web layer)
    │
    ▼
Application Service (use case orchestration)
    │
    ├──▶ Domain Entity (business rules, validation)
    │
    ├──▶ Repository (data persistence via interface)
    │
    ├──▶ AI Workflow (optional, for structuring/planning)
    │       │
    │       ▼
    │    LLM Provider (infrastructure adapter)
    │
    └──▶ Activity Event (append-only history)
    │
    ▼
Streamlit Page (UI) + FastAPI Route (API)
```

## Configuration

All configuration is environment-based. See `.env.example` for the full list. Secrets are never committed to source control.
