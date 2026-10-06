"""Application service for Idea management."""

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from idea_tracker.domain.exceptions import EntityNotFoundError
from idea_tracker.domain.models.activity import ActivityEvent
from idea_tracker.domain.models.idea import Idea, SourceEnum, StatusEnum


class IdeaService:
    """Service to handle business logic for Idea management."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_idea(self, title: str, raw_description: str, source: SourceEnum = SourceEnum.MANUAL) -> Idea:
        """Create a new idea and record the creation event."""
        idea = Idea(title=title, raw_description=raw_description, source=source, status=StatusEnum.INBOX)
        self.db.add(idea)
        self.db.commit()
        self.db.refresh(idea)

        self._record_event(idea.id, "IDEA_CREATED", {"title": title})
        return idea

    def get_idea(self, idea_id: int) -> Idea:
        """Retrieve an idea by ID."""
        idea = self.db.get(Idea, idea_id)
        if not idea:
            raise EntityNotFoundError("Idea", idea_id)
        return idea

    def update_status(self, idea_id: int, new_status: StatusEnum) -> Idea:
        """Update idea status and record the event."""
        idea = self.get_idea(idea_id)
        old_status = idea.status
        idea.status = new_status
        self.db.commit()
        self.db.refresh(idea)

        self._record_event(
            idea.id, "STATUS_CHANGED", {"old_status": old_status, "new_status": new_status}
        )
        return idea

    def _record_event(self, idea_id: int, event_type: str, metadata: dict[str, Any]) -> None:
        """Record an activity event."""
        event = ActivityEvent(
            idea_id=idea_id,
            event_type=event_type,
            event_metadata=json.dumps(metadata),
            timestamp=datetime.now(timezone.utc),
        )
        self.db.add(event)
        self.db.commit()
