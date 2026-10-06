# ADR-002: SQLite as Initial Database

## Status
Accepted

## Context
The application must be **local-first** and run effortlessly without requiring users to install or configure external database servers (like PostgreSQL, MySQL, or Redis). Data durability, transaction support, and full-text search are essential.

## Decision
We use **SQLite** (via SQLAlchemy 2.x and Alembic) as the default and primary database engine.

We enable:
- WAL mode (`PRAGMA journal_mode=WAL;`) for concurrent read/write performance.
- Foreign key constraints (`PRAGMA foreign_keys=ON;`).
- FTS5 extension for full-text keyword search across titles and descriptions.

The database access is abstracted behind repository interfaces defined in the domain layer, allowing for alternative database engines in the future if required.

## Consequences

### Positive
- **Zero configuration:** Runs as a single file on disk (`ideas.db`).
- **Local-first compliance:** Operates completely offline with no network dependency.
- **High performance:** In-process database with zero network latency; fast enough for thousands of ideas and tasks.
- **Embedded FTS5:** Full-text search built into the database engine without needing Elasticsearch or Meilisearch.

### Negative
- Single-writer limitation (mitigated by WAL mode and local single-user usage pattern).
- Less suited for large multi-tenant cloud deployments (out of scope for MVP).
