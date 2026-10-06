# Search Architecture

## Principles

1. Search works offline — no external service required for basic search.
2. The search interface is pluggable — implementations can be swapped without changing application code.
3. Start simple (FTS5), add sophistication only when needed.

## Phase 1: SQLite FTS5 + Indexed Queries

### What It Covers

- **Keyword search** across idea titles and descriptions
- **Title search** — exact and partial match
- **Description search** — full-text search via FTS5
- **Tag filtering** — filter by one or more tags
- **Status filtering** — filter by lifecycle state
- **Date filtering** — filter by created/updated date ranges
- **Combined filters** — any combination of the above

### FTS5 Setup

A virtual table mirrors the searchable text fields of ideas:

```sql
CREATE VIRTUAL TABLE ideas_fts USING fts5(
    title,
    raw_description,
    structured_description,
    content='ideas',
    content_rowid='id'
);
```

Kept in sync with triggers on the `ideas` table (insert, update, delete).

### Search Interface

```python
class SearchService(Protocol):
    async def search(
        self,
        query: str | None = None,
        *,
        tags: list[str] | None = None,
        status: list[str] | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> SearchResult: ...

@dataclass
class SearchResult:
    items: list[SearchHit]
    total: int
    query: str | None

@dataclass
class SearchHit:
    idea_id: int
    title: str
    snippet: str | None    # FTS5 highlight/snippet
    score: float | None    # Relevance score
```

### Phase 1 Implementation

```
infrastructure/search/
├── base.py              # SearchService protocol, SearchResult, SearchHit
└── sqlite_search.py     # FTS5-backed implementation
```

## Future: Semantic Search

### Phase 2: Local Embeddings

When basic keyword search proves insufficient, add:

```python
class EmbeddingProvider(Protocol):
    async def embed(self, text: str) -> list[float]: ...
    async def embed_batch(self, texts: list[str]) -> list[list[float]]: ...
```

Potential providers:
- Ollama embeddings (local)
- sentence-transformers (local, Python-native)
- OpenAI embeddings (cloud)

### Phase 3: Vector Index

Pluggable vector search backend:

```python
class VectorSearchProvider(Protocol):
    async def index(self, id: str, embedding: list[float], metadata: dict) -> None: ...
    async def search(self, query_embedding: list[float], *, limit: int = 10) -> list[VectorHit]: ...
```

Potential backends:
- SQLite-based (e.g., sqlite-vec or manual cosine similarity for small datasets)
- turbovec (local, file-based)
- No external vector databases in initial versions

### Phase 3: Hybrid Search

Combine keyword and semantic results:

```python
class HybridSearchProvider:
    def __init__(
        self,
        keyword: KeywordSearchProvider,
        semantic: SemanticSearchProvider,
    ): ...
```

Uses reciprocal rank fusion or similar to merge results.

## Capabilities This Enables

Once semantic search is in place:

- "Have I had a similar idea before?"
- "Show me ideas related to AI and exporters"
- "Which abandoned ideas could now be feasible?"
- "Which ideas share the same underlying problem?"
- Automatic duplicate/similar idea detection on capture

These are future features — the architecture supports them without coupling the MVP to a vector database.
