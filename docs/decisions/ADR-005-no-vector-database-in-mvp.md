# ADR-005: No Vector Database in MVP

## Status
Accepted

## Context
Semantic search and similarity detection (e.g., "Find ideas similar to this one") are valuable long-term capabilities. Vector databases (Chroma, Qdrant, Pinecone, Weaviate) are common solutions for vector search.

However, adding a dedicated vector database into the initial MVP adds significant operational complexity, binary dependencies, memory overhead, and setup friction.

## Decision
We **defer vector databases and local embedding indexes** from the MVP release.

- Phase 1 relies exclusively on **SQLite FTS5** for keyword and full-text search.
- We design the search interface (`SearchService` protocol) so that a hybrid or semantic search provider can be added cleanly in a future phase without breaking existing code.

Future semantic capabilities will explore lightweight embedded solutions (e.g., `sqlite-vec` or in-memory numpy cosine similarity) before considering standalone vector databases.

## Consequences

### Positive
- **Zero extra dependencies:** Keeps the installation footprint small and fast.
- **Reduced operational complexity:** No extra service containers, volume management, or vector index rebuild logic in MVP.
- **Focus on core product loop:** Engineering effort remains focused on capture, structure, validation, decision, and execution loops.

### Negative
- Conceptual search (finding related ideas without shared keywords) is unavailable in MVP.
- "Similar ideas" detection relies on manual tagging or category filtering until semantic search is added.
