"""Tests for IdeaService."""

from idea_tracker.application.services.idea_service import IdeaService
from idea_tracker.domain.models.idea import StatusEnum
from sqlalchemy.orm import Session

def test_create_and_get_idea(db_session: Session) -> None:
    """Verify idea creation and retrieval via service."""
    service = IdeaService(db_session)
    idea = service.create_idea("Test Idea", "Description")

    retrieved = service.get_idea(idea.id)
    assert retrieved.title == "Test Idea"
    assert retrieved.status == StatusEnum.INBOX
    assert len(retrieved.events) == 1
    assert retrieved.events[0].event_type == "IDEA_CREATED"

def test_update_status(db_session: Session) -> None:
    """Verify status update and event recording."""
    service = IdeaService(db_session)
    idea = service.create_idea("Test Idea", "Description")

    updated = service.update_status(idea.id, StatusEnum.STRUCTURED)

    assert updated.status == StatusEnum.STRUCTURED
    assert len(updated.events) == 2
    assert updated.events[1].event_type == "STATUS_CHANGED"
    assert "STRUCTURED" in updated.events[1].event_metadata
