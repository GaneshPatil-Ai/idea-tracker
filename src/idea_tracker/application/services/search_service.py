"""Search service using SQLite keyword and full-text capabilities."""

from datetime import datetime, UTC

from sqlalchemy import and_, func, or_, text
from sqlalchemy.orm import Session

from idea_tracker.domain.exceptions import EntityNotFoundError
from idea_tracker.domain.models.activity import ActivityEvent
from idea_tracker.domain.models.content import Note, Tag
from idea_tracker.domain.models.decision import Decision
from idea_tracker.domain.models.execution import Milestone, Task
from idea_tracker.domain.models.idea import Idea
from idea_tracker.domain.models.research import ResearchEvidence, ResearchQuestion


class SearchService:
    """Service for searching ideas using keyword and full-text search."""

    def __init__(self, db: Session):
        self.db = db

    def search_ideas(
        self,
        query: str,
        search_type: str = "hybrid",
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        """Search ideas using keyword or full-text search.

        Args:
            query: Search term
            search_type: 'keyword' (exact), 'full_text' (LIKE), or 'hybrid' (both)
            limit: Maximum results
            offset: Pagination offset

        Returns:
            Dict with results and metadata
        """
        if not query or len(query.strip()) == 0:
            raise ValueError("Search query cannot be empty")

        query_lower = f"%{query.lower()}%"

        if search_type == "keyword":
            results = self._keyword_search(query, limit, offset)
        elif search_type == "full_text":
            results = self._fulltext_search(query_lower, limit, offset)
        else:  # hybrid
            results = self._hybrid_search(query, query_lower, limit, offset)

        return {
            "query": query,
            "search_type": search_type,
            "results": results,
            "total": len(results),
            "limit": limit,
            "offset": offset,
        }

    def _keyword_search(self, query: str, limit: int, offset: int) -> list[dict]:
        """Exact keyword match search."""
        ideas = (
            self.db.query(Idea)
            .filter(or_(Idea.title.ilike(f"%{query}%"), Idea.raw_description.ilike(f"%{query}%")))
            .order_by(Idea.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return self._format_results(ideas)

    def _fulltext_search(self, query_lower: str, limit: int, offset: int) -> list[dict]:
        """Full-text search across all idea content."""
        ideas = (
            self.db.query(Idea)
            .filter(
                or_(
                    Idea.title.ilike(query_lower),
                    Idea.raw_description.ilike(query_lower),
                    Idea.structured_description.ilike(query_lower),
                )
            )
            .order_by(Idea.updated_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return self._format_results(ideas)

    def _hybrid_search(self, query: str, query_lower: str, limit: int, offset: int) -> list[dict]:
        """Hybrid search combining keyword and full-text."""
        ideas = (
            self.db.query(Idea)
            .filter(
                or_(
                    Idea.title.ilike(query_lower),
                    Idea.raw_description.ilike(query_lower),
                    Idea.structured_description.ilike(query_lower),
                )
            )
            .order_by(Idea.updated_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return self._format_results(ideas)

    def search_by_tag(self, tag_name: str, limit: int = 20, offset: int = 0) -> dict:
        """Search ideas by tag."""
        tag = self.db.query(Tag).filter(Tag.name.ilike(tag_name)).first()
        if not tag:
            return {"tag": tag_name, "results": [], "total": 0}

        ideas = (
            self.db.query(Idea)
            .filter(Idea.tags.any(Tag.id == tag.id))
            .order_by(Idea.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return {
            "tag": tag_name,
            "results": self._format_results(ideas),
            "total": len(ideas),
        }

    def search_by_status(self, status: str, limit: int = 20, offset: int = 0) -> dict:
        """Search ideas by status."""
        ideas = (
            self.db.query(Idea)
            .filter(Idea.status == status)
            .order_by(Idea.updated_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return {
            "status": status,
            "results": self._format_results(ideas),
            "total": len(ideas),
        }

    def search_decisions_by_outcome(self, outcome: str, limit: int = 20) -> dict:
        """Search decisions by outcome."""
        decisions = (
            self.db.query(Decision)
            .filter(Decision.outcome == outcome)
            .order_by(Decision.created_at.desc())
            .limit(limit)
            .all()
        )
        return {
            "outcome": outcome,
            "results": [
                {
                    "id": d.id,
                    "idea_id": d.idea_id,
                    "title": d.title,
                    "outcome": d.outcome.value,
                    "created_at": d.created_at.isoformat(),
                }
                for d in decisions
            ],
            "total": len(decisions),
        }

    def get_related_ideas(self, idea_id: int) -> dict:
        """Get related ideas based on shared tags."""
        idea = self.db.get(Idea, idea_id)
        if not idea:
            raise EntityNotFoundError("Idea", idea_id)

        if not idea.tags:
            return {"idea_id": idea_id, "related": []}

        tag_ids = [tag.id for tag in idea.tags]
        related = (
            self.db.query(Idea)
            .filter(
                and_(Idea.id != idea_id, Idea.tags.any(Tag.id.in_(tag_ids)))
            )
            .order_by(Idea.updated_at.desc())
            .limit(10)
            .all()
        )
        return {
            "idea_id": idea_id,
            "related": self._format_results(related),
        }

    def _format_results(self, ideas: list[Idea]) -> list[dict]:
        """Format idea objects for API response."""
        return [
            {
                "id": idea.id,
                "title": idea.title,
                "status": idea.status.value,
                "created_at": idea.created_at.isoformat(),
                "updated_at": idea.updated_at.isoformat(),
                "tags": [tag.name for tag in idea.tags],
            }
            for idea in ideas
        ]
