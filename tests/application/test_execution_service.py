"""Tests for ExecutionService."""

from idea_tracker.application.services.execution_service import ExecutionService
from sqlalchemy.orm import Session


def test_create_milestone(db_session: Session) -> None:
    """Verify milestone creation for an idea."""
    service = ExecutionService(db_session)
    idea = service.create_milestone  # placeholder to ensure idea service available

    # use the existing service through shared session
    from idea_tracker.application.services.idea_service import IdeaService

    idea_svc = IdeaService(db_session)
    idea = idea_svc.create_idea("Test Idea", "Description")

    milestone = service.create_milestone(idea.id, "Research Phase")
    assert milestone.idea_id == idea.id
    assert milestone.title == "Research Phase"
    assert milestone.position == 0
    assert milestone.status == "TODO"


def test_complete_milestone(db_session: Session) -> None:
    """Verify milestone completion updates timestamp."""
    from idea_tracker.application.services.idea_service import IdeaService

    idea_svc = IdeaService(db_session)
    idea = idea_svc.create_idea("Test Idea", "Description")
    service = ExecutionService(db_session)

    milestone = service.create_milestone(idea.id, "Research Phase")
    completed = service.complete_milestone(milestone.id)
    assert completed.status == "DONE"
    assert completed.completed_at is not None


def test_create_task(db_session: Session) -> None:
    """Verify task creation under a milestone."""
    from idea_tracker.application.services.idea_service import IdeaService

    idea_svc = IdeaService(db_session)
    idea = idea_svc.create_idea("Test Idea", "Description")
    service = ExecutionService(db_session)
    milestone = service.create_milestone(idea.id, "Research Phase")

    task = service.create_task(milestone.id, "Interview users", priority="HIGH")
    assert task.milestone_id == milestone.id
    assert task.priority == "HIGH"
    assert task.status == "TODO"


def test_complete_task(db_session: Session) -> None:
    """Verify task completion records event."""
    from idea_tracker.application.services.idea_service import IdeaService

    idea_svc = IdeaService(db_session)
    idea = idea_svc.create_idea("Test Idea", "Description")
    service = ExecutionService(db_session)
    milestone = service.create_milestone(idea.id, "Research Phase")
    task = service.create_task(milestone.id, "Interview users")

    completed = service.complete_task(task.id)
    assert completed.status == "DONE"
    assert completed.completed_at is not None

    # activity event recorded
    retrieved_idea = idea_svc.get_idea(idea.id)
    event_types = [e.event_type for e in retrieved_idea.events]
    assert "TASK_COMPLETED" in event_types
