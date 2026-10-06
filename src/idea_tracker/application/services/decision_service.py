"""Service for managing decisions."""

from datetime import datetime, UTC

from sqlalchemy.orm import Session

from idea_tracker.domain.exceptions import EntityNotFoundError
from idea_tracker.domain.models.activity import ActivityEvent
from idea_tracker.domain.models.decision import Decision, DecisionOutcome
from idea_tracker.domain.models.idea import Idea


class DecisionService:
    """Service to handle business logic for decisions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_decision(
        self,
        idea_id: int,
        title: str,
        outcome: DecisionOutcome,
        rationale: str,
    ) -> Decision:
        """Record a formal decision for an idea."""
        self.get_idea(idea_id)  # Validate idea exists
        decision = Decision(
            idea_id=idea_id,
            title=title,
            outcome=outcome,
            rationale=rationale,
        )
        self.db.add(decision)
        self.db.commit()
        self.db.refresh(decision)

        self._record_event(
            idea_id,
            "DECISION_MADE",
            {
                "decision_id": decision.id,
                "outcome": outcome.value,
                "title": title,
            },
        )
        return decision

    def get_decisions_for_idea(self, idea_id: int) -> list[Decision]:
        """Retrieve all decisions for a given idea."""
        self.get_idea(idea_id)  # Validate idea exists
        return (
            self.db.query(Decision)
            .filter(Decision.idea_id == idea_id)
            .order_by(Decision.created_at.desc())
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
            timestamp=datetime.now(UTC),
        )
        self.db.add(event)
        self.db.commit()
