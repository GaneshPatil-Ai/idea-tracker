"""Tests for domain exceptions."""

from idea_tracker.domain.exceptions import (
    AIServiceError,
    EntityNotFoundError,
    IdeaTrackerError,
    InvalidTransitionError,
)


def test_entity_not_found_error_message() -> None:
    """Verify EntityNotFoundError formats message correctly."""
    err = EntityNotFoundError("Idea", 42)
    assert "Idea" in str(err)
    assert "42" in str(err)
    assert isinstance(err, IdeaTrackerError)


def test_invalid_transition_error_message() -> None:
    """Verify InvalidTransitionError includes state names."""
    err = InvalidTransitionError("INBOX", "BUILDING", reason="Must structure first")
    assert "INBOX" in str(err)
    assert "BUILDING" in str(err)
    assert "Must structure first" in str(err)


def test_ai_service_error() -> None:
    """Verify AIServiceError preserves raw response."""
    err = AIServiceError("JSON parse failed", raw_response="{bad json}")
    assert err.raw_response == "{bad json}"
    assert "JSON parse failed" in str(err)
