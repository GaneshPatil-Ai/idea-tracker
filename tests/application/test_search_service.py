"""Tests for search service."""

import pytest
from sqlalchemy.orm import Session

from idea_tracker.application.services.idea_service import IdeaService
from idea_tracker.application.services.search_service import SearchService
from idea_tracker.application.services.decision_service import DecisionService
from idea_tracker.domain.models.decision import DecisionOutcome
from idea_tracker.domain.models.content import Tag
from idea_tracker.domain.exceptions import EntityNotFoundError


def test_search_ideas_keyword(db_session: Session):
    """Test keyword search for ideas."""
    # Create ideas
    idea_service = IdeaService(db_session)
    idea1 = idea_service.create_idea("Python Web Framework", "A new web framework for Python")
    idea2 = idea_service.create_idea("JavaScript Library", "A new JavaScript library")

    # Search for "Python"
    search_service = SearchService(db_session)
    results = search_service.search_ideas("Python", search_type="keyword")

    assert results["total"] == 1
    assert results["results"][0]["id"] == idea1.id
    assert "Python" in results["results"][0]["title"]


def test_search_ideas_full_text(db_session: Session):
    """Test full-text search for ideas."""
    # Create ideas
    idea_service = IdeaService(db_session)
    idea1 = idea_service.create_idea("API Design", "REST API best practices")
    idea2 = idea_service.create_idea("Database Optimization", "SQL query optimization techniques")

    # Search for "API"
    search_service = SearchService(db_session)
    results = search_service.search_ideas("API", search_type="full_text")

    assert results["total"] == 1
    assert results["results"][0]["id"] == idea1.id


def test_search_ideas_hybrid(db_session: Session):
    """Test hybrid search combining keyword and full-text."""
    # Create ideas
    idea_service = IdeaService(db_session)
    idea1 = idea_service.create_idea("ML Model Design", "Neural network architecture")
    idea2 = idea_service.create_idea("Data Pipeline", "ML data processing pipeline")

    # Search for "ML" — both ideas contain "ML" in title or description
    search_service = SearchService(db_session)
    results = search_service.search_ideas("ML", search_type="hybrid")

    assert results["total"] == 2


def test_search_by_tag(db_session: Session):
    """Test searching ideas by tag."""
    # Create ideas with tags
    idea_service = IdeaService(db_session)
    idea1 = idea_service.create_idea("Idea 1", "Description 1")
    idea2 = idea_service.create_idea("Idea 2", "Description 2")

    # Add tags
    tag1 = Tag(name="ai")
    tag2 = Tag(name="web")
    idea1.tags.append(tag1)
    idea2.tags.append(tag2)
    db_session.commit()

    # Search by tag
    search_service = SearchService(db_session)
    results = search_service.search_by_tag("ai")

    assert results["total"] == 1
    assert results["results"][0]["id"] == idea1.id
    assert "ai" in results["results"][0]["tags"]


def test_search_by_status(db_session: Session):
    """Test searching ideas by status."""
    # Create ideas
    idea_service = IdeaService(db_session)
    idea1 = idea_service.create_idea("Idea 1", "Description 1")
    idea2 = idea_service.create_idea("Idea 2", "Description 2")

    # Update status
    idea_service.update_status(idea1.id, "EXPLORING")

    # Search by status
    search_service = SearchService(db_session)
    results = search_service.search_by_status("EXPLORING")

    assert results["total"] == 1
    assert results["results"][0]["id"] == idea1.id


def test_search_decisions_by_outcome(db_session: Session):
    """Test searching decisions by outcome."""
    # Create idea and decisions
    idea_service = IdeaService(db_session)
    idea = idea_service.create_idea("Test Idea", "Description")

    decision_service = DecisionService(db_session)
    decision1 = decision_service.create_decision(
        idea.id, "Go Decision", DecisionOutcome.GO, "Looks good"
    )
    decision2 = decision_service.create_decision(
        idea.id, "No-Go Decision", DecisionOutcome.NO_GO, "Too risky"
    )

    # Search by outcome
    search_service = SearchService(db_session)
    results = search_service.search_decisions_by_outcome("GO")

    assert results["total"] == 1
    assert results["results"][0]["id"] == decision1.id


def test_get_related_ideas(db_session: Session):
    """Test getting related ideas based on shared tags."""
    # Create ideas with shared tags
    idea_service = IdeaService(db_session)
    idea1 = idea_service.create_idea("Idea 1", "Description 1")
    idea2 = idea_service.create_idea("Idea 2", "Description 2")
    idea3 = idea_service.create_idea("Idea 3", "Description 3")

    # Add tags
    tag1 = Tag(name="python")
    tag2 = Tag(name="web")
    tag3 = Tag(name="database")

    idea1.tags.extend([tag1, tag2])
    idea2.tags.append(tag1)  # Shares "python" with idea1
    idea3.tags.append(tag3)  # No shared tags

    db_session.commit()

    # Get related ideas for idea1
    search_service = SearchService(db_session)
    results = search_service.get_related_ideas(idea1.id)

    assert len(results["related"]) == 1
    assert results["related"][0]["id"] == idea2.id


def test_search_with_pagination(db_session: Session):
    """Test search with pagination."""
    # Create multiple ideas
    idea_service = IdeaService(db_session)
    for i in range(5):
        idea_service.create_idea(f"Test Idea {i}", f"Description {i}")

    # Search with pagination
    search_service = SearchService(db_session)
    results = search_service.search_ideas("Test", limit=2, offset=0)

    assert results["total"] == 2
    assert results["limit"] == 2
    assert results["offset"] == 0


def test_search_empty_query(db_session: Session):
    """Test search with empty query raises error."""
    search_service = SearchService(db_session)

    with pytest.raises(ValueError, match="Search query cannot be empty"):
        search_service.search_ideas("")


def test_search_nonexistent_idea_for_related(db_session: Session):
    """Test getting related ideas for non-existent idea."""
    search_service = SearchService(db_session)

    with pytest.raises(EntityNotFoundError):
        search_service.get_related_ideas(999)
