# ADR-001: Modular Monolith Architecture

## Status
Accepted

## Context
The Idea Tracker is a local-first application meant to be run by individuals or small teams on their own machines or simple servers. The domain spans several closely related concepts: ideas, execution (milestones/tasks), research, validation, decisions, reviews, AI workflows, search, and notifications.

We need to decide on the high-level system architecture: microservices vs. modular monolith vs. unstructured monolith.

## Decision
We choose a **modular monolith** architecture.

The code is organized into a single deployable Python package with strict internal module boundaries:

```
Web / API Layer
    ↓
Application Layer (Use Cases)
    ↓
Domain Layer (Entities, Rules, Interfaces)
    ↑
Infrastructure Layer (Database, LLM, Search adapters)
```

The domain layer has zero dependencies on frameworks, ORMs, HTTP clients, or external services.

## Consequences

### Positive
- **Single deployable unit:** Easy to run locally, package, and deploy via Docker or `uv`.
- **Zero network overhead:** Inter-module calls are standard Python function calls, avoiding serialization, network latency, and partial failure modes of microservices.
- **Clear boundaries:** Keeps code organized and testable; modules can be refactored or extracted later if genuinely needed.
- **Simplified data management:** All modules share a single SQLite database with consistent transaction boundaries.

### Negative
- Require strict discipline to prevent cross-module leaks (enforced by linting and architectural reviews).
- Cannot scale individual modules independently (not a requirement for local-first software).
