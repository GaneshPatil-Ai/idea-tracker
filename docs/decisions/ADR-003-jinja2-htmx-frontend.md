# ADR-003: Jinja2 + HTMX Frontend Stack

## Status
Accepted

## Context
We need an interactive, responsive user interface for capturing, structuring, validating, and executing ideas. Modern single-page application (SPA) frameworks like React, Vue, or Next.js introduce significant build complexity (Node.js, npm, webpack/vite, bundlers) and separate backend/frontend deployments.

## Decision
We use **Jinja2 server-rendered templates** enhanced with **HTMX** for dynamic, SPA-like interactions, styled with modern vanilla CSS.

- **FastAPI + Jinja2:** Renders full pages and partial HTML snippets.
- **HTMX:** Handles asynchronous form submissions, inline editing, modal dialogs, status updates, and filter changes without full page reloads.
- **Vanilla JS:** Minimal script tags only where HTMX cannot cleanly cover (e.g., keyboard shortcuts).

No Node.js, npm, or frontend build pipelines are required.

## Consequences

### Positive
- **Single language:** Entire codebase is written in Python (HTML templates use Jinja2 syntax).
- **Simpler toolchain:** No `node_modules`, package managers for JS, or build step. Fast development feedback loop.
- **Smaller bundle size:** Browser loads lightweight HTMX library (~14KB minified/gzipped); initial page renders are fast server-rendered HTML.
- **Maintainability:** Easy for backend/full-stack Python developers to read, write, and maintain.

### Negative
- Offline dynamic behavior (in-browser state logic) is more limited than a full SPA.
- Rich drag-and-drop or complex canvas UI requires custom vanilla JS or external light libraries.
