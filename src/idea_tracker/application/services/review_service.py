"""Service for managing idea reviews and detecting stale ideas."""

from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy.orm import Session

from idea_tracker.domain.models.activity import ActivityEvent
from idea_tracker.domain.models.idea import Idea, StatusEnum
from idea_tracker.domain.exceptions import EntityNotFoundError


class ReviewService:
    """Service to handle reviews and stale idea detection."""

    STALE_DAYS = 14  # Ideas not reviewed in 14 days are stale

    def __init__(self, db: Session) -> None:
        self.db = db

    def mark_idea_reviewed(self, idea_id: int) -> Idea:
        """Mark an idea as reviewed."""
        idea = self.get_idea(idea_id)
        idea.last_reviewed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(idea)

        self._record_event(idea_id, "IDEA_REVIEWED", {"reviewed_at": idea.last_reviewed_at.isoformat()})
        return idea

    def get_stale_ideas(self) -> List[Idea]:
        """Get all ideas that haven't been reviewed in STALE_DAYS."""
        threshold = datetime.now(timezone.utc) - timedelta(days=self.STALE_DAYS)
        return (
            self.db.query(Idea)
            .filter(
                (Idea.last_reviewed_at.is_(None)) | (Idea.last_reviewed_at < threshold)
            )
            .filter(Idea.status != StatusEnum.KILLED)
            .filter(Idea.status != StatusEnum.LAUNCHED)
            .order_by(Idea.last_reviewed_at.asc())
            .all()
        )

    def get_idea(self, idea_id: int) -> Idea:
        """Retrieve an idea by ID, raising if not found."""
        idea = self.db.get(Idea, idea_id)
        if not idea:
            raise EntityNotFoundError("Idea", idea_id)
        return idea

    def _record_event(self, idea_id: int, event_type: str, metadata: dict) -> None:
        """Record an activity event for an idea."""
        event = ActivityEvent(
            idea_id=idea_id,
            event_type=event_type,
            event_metadata=__import__("json").dumps(metadata),
            timestamp=datetime.now(timezone.utc),
        )
        self.db.add(event)
        self.db.commit()
