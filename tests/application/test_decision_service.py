"""Tests for decision service."""

import pytest
from sqlalchemy.orm import Session

from idea_tracker.application.services.decision_service import DecisionService
from idea_tracker.application.services.idea_service import IdeaService
from idea_tracker.domain.models.decision import DecisionOutcome
from idea_tracker.domain.exceptions import EntityNotFoundError


def test_create_decision(db_session: Session):
    """Test creating a decision for an idea."""
    # Create an idea first
    idea_service = IdeaService(db_session)
    idea = idea_service.create_idea("Test Idea", "A test idea description")

    # Create a decision
    decision_service = DecisionService(db_session)
    decision = decision_service.create_decision(
        idea.id, "Go/No-Go Decision", DecisionOutcome.GO, "This looks promising"
    )

    assert decision.id is not None
    assert decision.idea_id == idea.id
    assert decision.title == "Go/No-Go Decision"
    assert decision.outcome == DecisionOutcome.GO
    assert decision.rationale == "This looks promising"
    assert decision.created_at is not None


def test_get_decisions_for_idea(db_session: Session):
    """Test retrieving all decisions for an idea."""
    # Create an idea
    idea_service = IdeaService(db_session)
    idea = idea_service.create_idea("Test Idea", "A test idea description")

    # Create multiple decisions
    decision_service = DecisionService(db_session)
    decision1 = decision_service.create_decision(
        idea.id, "Initial Assessment", DecisionOutcome.GO, "Looks good"
    )
    decision2 = decision_service.create_decision(
        idea.id, "Final Decision", DecisionOutcome.NO_GO, "Market too small"
    )

    # Retrieve decisions
    decisions = decision_service.get_decisions_for_idea(idea.id)

    assert len(decisions) == 2
    # Should be ordered by created_at desc (newest first)
    assert decisions[0].id == decision2.id
    assert decisions[1].id == decision1.id


def test_create_decision_for_nonexistent_idea(db_session: Session):
    """Test creating a decision for a non-existent idea raises error."""
    decision_service = DecisionService(db_session)

    with pytest.raises(EntityNotFoundError):
        decision_service.create_decision(
            999, "Test Decision", DecisionOutcome.GO, "This should fail"
        )


def test_get_decisions_for_nonexistent_idea(db_session: Session):
    """Test getting decisions for a non-existent idea raises error."""
    decision_service = DecisionService(db_session)

    with pytest.raises(EntityNotFoundError):
        decision_service.get_decisions_for_idea(999)