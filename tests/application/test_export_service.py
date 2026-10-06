"""Tests for export service."""

import json

import pytest
from sqlalchemy.orm import Session

from idea_tracker.application.services.export_service import ExportService
from idea_tracker.application.services.idea_service import IdeaService
from idea_tracker.application.services.decision_service import DecisionService
from idea_tracker.domain.models.content import Tag
from idea_tracker.domain.models.decision import DecisionOutcome


def test_export_all_ideas_json(db_session: Session):
    """Test exporting all ideas to JSON."""
    # Create test ideas
    idea_service = IdeaService(db_session)
    idea1 = idea_service.create_idea("Idea 1", "Description 1")
    idea2 = idea_service.create_idea("Idea 2", "Description 2")

    # Export to JSON
    export_service = ExportService(db_session)
    result = export_service.export_all_ideas(format="json")

    # Parse and validate
    data = json.loads(result)
    assert data["total_ideas"] == 2
    assert len(data["ideas"]) == 2
    assert data["ideas"][0]["title"] in ["Idea 1", "Idea 2"]


def test_export_all_ideas_markdown(db_session: Session):
    """Test exporting all ideas to markdown."""
    # Create test ideas
    idea_service = IdeaService(db_session)
    idea1 = idea_service.create_idea("Idea 1", "Description 1")

    # Export to markdown
    export_service = ExportService(db_session)
    result = export_service.export_all_ideas(format="markdown")

    # Validate markdown content
    assert "# Idea Tracker Export" in result
    assert "## Idea 1" in result
    assert "Description 1" in result


def test_export_single_idea_json(db_session: Session):
    """Test exporting single idea to JSON."""
    # Create idea with tags and decision
    idea_service = IdeaService(db_session)
    idea = idea_service.create_idea("Test Idea", "Test description")

    # Add tag
    tag = Tag(name="test-tag")
    idea.tags.append(tag)
    db_session.commit()

    # Add decision
    decision_service = DecisionService(db_session)
    decision_service.create_decision(
        idea.id, "Go/No-Go", DecisionOutcome.GO, "Looks promising"
    )

    # Export to JSON
    export_service = ExportService(db_session)
    result = export_service.export_idea(idea.id, format="json")

    # Parse and validate
    data = json.loads(result)
    assert data["idea"]["title"] == "Test Idea"
    assert "test-tag" in data["idea"]["tags"]
    assert len(data["idea"]["decisions"]) == 1
    assert data["idea"]["decisions"][0]["outcome"] == "GO"


def test_export_single_idea_markdown(db_session: Session):
    """Test exporting single idea to markdown."""
    # Create idea
    idea_service = IdeaService(db_session)
    idea = idea_service.create_idea("Markdown Idea", "Markdown description")

    # Export to markdown
    export_service = ExportService(db_session)
    result = export_service.export_idea(idea.id, format="markdown")

    # Validate markdown content
    assert "## Markdown Idea" in result
    assert "Markdown description" in result
    assert "**Status**:" in result


def test_export_idea_with_complete_data(db_session: Session):
    """Test exporting idea with all relationships populated."""
    # Create comprehensive idea
    idea_service = IdeaService(db_session)
    idea = idea_service.create_idea("Complete Idea", "Full description")

    # Add tags
    tag1 = Tag(name="python")
    tag2 = Tag(name="web")
    idea.tags.extend([tag1, tag2])
    db_session.commit()

    # Add decision
    decision_service = DecisionService(db_session)
    decision_service.create_decision(
        idea.id, "Architecture Decision", DecisionOutcome.PIVOT, "Need to change approach"
    )

    # Export
    export_service = ExportService(db_session)
    result = export_service.export_idea(idea.id, format="json")

    # Validate
    data = json.loads(result)
    assert len(data["idea"]["tags"]) == 2
    assert "python" in data["idea"]["tags"]
    assert len(data["idea"]["decisions"]) == 1


def test_export_invalid_format(db_session: Session):
    """Test export with invalid format raises error."""
    export_service = ExportService(db_session)

    with pytest.raises(ValueError, match="Unsupported format"):
        export_service.export_all_ideas(format="xml")


def test_export_nonexistent_idea(db_session: Session):
    """Test exporting non-existent idea raises error."""
    export_service = ExportService(db_session)

    with pytest.raises(ValueError, match="Idea 999 not found"):
        export_service.export_idea(999, format="json")


def test_export_empty_database(db_session: Session):
    """Test exporting from empty database."""
    export_service = ExportService(db_session)
    result = export_service.export_all_ideas(format="json")

    data = json.loads(result)
    assert data["total_ideas"] == 0
    assert len(data["ideas"]) == 0
