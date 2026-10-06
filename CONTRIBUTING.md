# Contributing to Idea Tracker

Thank you for your interest in contributing! Idea Tracker is designed as an open-source, local-first system.

## Principles for Contributions

1. **Local-first** — Never depend on external cloud infrastructure for core features.
2. **Modular Monolith** — Keep layer boundaries clean (`Web` → `Application` → `Domain` ← `Infrastructure`).
3. **Simplicity First** — Write surgical, minimal code that solves the problem. No speculative abstractions.
4. **Verifiable Quality** — Every change must include tests and pass `ruff` + `mypy`.

## Getting Started

1. Fork and clone the repository.
2. Setup environment using `uv`:
   ```bash
   uv sync --extra dev
   ```
3. Run tests and linting to verify setup:
   ```bash
   make check
   ```

## Pull Request Checklist

Before submitting a PR:
- [ ] Code follows project architecture (modular monolith, clean domain separation).
- [ ] `uv run pytest` passes.
- [ ] `uv run ruff check .` passes.
- [ ] `uv run mypy src` passes.
- [ ] Database migrations are created via Alembic if schema changed (`uv run alembic revision --autogenerate -m "..."`).
- [ ] Documentation or ADR updated if applicable.
