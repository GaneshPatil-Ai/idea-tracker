"""Tests for review service."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.orm import Session

from idea_tracker.application.services.review_service import ReviewService
from idea_tracker.application.services.idea_service import IdeaService
from idea_tracker.domain.models.idea import StatusEnum


def test_mark_idea_reviewed(db_session: Session):
    """Test marking an idea as reviewed."""
    # Create an idea
    idea_service = IdeaService(db_session)
    idea = idea_service.create_idea("Test Idea", "A test idea description")
    assert idea.last_reviewed_at is None

    # Mark as reviewed
    review_service = ReviewService(db_session)
    idea = review_service.mark_idea_reviewed(idea.id)

    # Verify timestamp was updated
    assert idea.last_reviewed_at is not None
    # Should be within the last few seconds
    now = datetime.now(timezone.utc)
    # Note: DB may return timezone-naive, so compare to naive version
    reviewed_at = idea.last_reviewed_at
    if reviewed_at.tzinfo is not None:
        reviewed_at = reviewed_at.replace(tzinfo=None)
    time_diff = now.replace(tzinfo=None) - reviewed_at
    assert time_diff.total_seconds() < 2


def test_get_stale_ideas(db_session: Session):
    """Test detecting stale ideas."""
    # Create multiple ideas
    idea_service = IdeaService(db_session)
    review_service = ReviewService(db_session)

    # Fresh idea (reviewed today)
    fresh_idea = idea_service.create_idea("Fresh Idea", "Recently reviewed")
    fresh_idea = review_service.mark_idea_reviewed(fresh_idea.id)

    # Old idea (reviewed 15 days ago - beyond stale threshold)
    old_idea = idea_service.create_idea("Old Idea", "Old review")
    old_idea.last_reviewed_at = datetime.now(timezone.utc) - timedelta(days=15)
    db_session.commit()

    # Never reviewed idea
    never_reviewed = idea_service.create_idea("Never Reviewed", "No review")

    # Killed idea (should not appear in stale list)
    killed_idea = idea_service.create_idea("Killed Idea", "Already killed")
    idea_service.update_status(killed_idea.id, StatusEnum.KILLED)

    # Get stale ideas
    stale = review_service.get_stale_ideas()

    # Should include old_idea and never_reviewed, but not fresh_idea or killed_idea
    stale_ids = {i.id for i in stale}
    assert old_idea.id in stale_ids
    assert never_reviewed.id in stale_ids
    assert fresh_idea.id not in stale_ids
    assert killed_idea.id not in stale_ids


def test_mark_nonexistent_idea_reviewed(db_session: Session):
    """Test marking a non-existent idea as reviewed raises error."""
    review_service = ReviewService(db_session)

    with pytest.raises(Exception):
        review_service.mark_idea_reviewed(999)