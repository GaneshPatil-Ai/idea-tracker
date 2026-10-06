"""Tests for research service."""

from datetime import datetime, UTC

import pytest
from sqlalchemy.orm import Session

from idea_tracker.application.services.idea_service import IdeaService
from idea_tracker.application.services.research_service import ResearchService
from idea_tracker.domain.exceptions import EntityNotFoundError
from idea_tracker.domain.models.research import EvidenceType


def test_add_evidence(db_session: Session):
    """Test adding research evidence to an idea."""
    # Create an idea first
    idea_service = IdeaService(db_session)
    idea = idea_service.create_idea("Test Idea", "A test idea description")

    # Add evidence
    research_service = ResearchService(db_session)
    evidence = research_service.add_evidence(
        idea.id,
        "Important Research Paper",
        "https://example.com/paper.pdf",
        EvidenceType.ARTICLE,
        author="Jane Researcher",
        summary="Key findings about the market",
    )

    assert evidence.id is not None
    assert evidence.idea_id == idea.id
    assert evidence.title == "Important Research Paper"
    assert evidence.url == "https://example.com/paper.pdf"
    assert evidence.evidence_type == EvidenceType.ARTICLE
    assert evidence.author == "Jane Researcher"
    assert evidence.summary == "Key findings about the market"
    assert evidence.created_at is not None


def test_get_evidence_for_idea(db_session: Session):
    """Test retrieving all evidence for an idea."""
    # Create an idea
    idea_service = IdeaService(db_session)
    idea = idea_service.create_idea("Test Idea", "A test idea description")

    # Add multiple pieces of evidence
    research_service = ResearchService(db_session)
    evidence1 = research_service.add_evidence(
        idea.id, "Article 1", "https://example.com/1", EvidenceType.ARTICLE
    )
    evidence2 = research_service.add_evidence(
        idea.id, "Video 1", "https://youtube.com/watch?v=123", EvidenceType.VIDEO
    )

    # Retrieve evidence
    evidence_list = research_service.get_evidence_for_idea(idea.id)

    assert len(evidence_list) == 2
    # Should be ordered by created_at desc (newest first)
    assert evidence_list[0].id == evidence2.id
    assert evidence_list[1].id == evidence1.id


def test_add_research_question(db_session: Session):
    """Test adding a research question to an idea."""
    # Create an idea
    idea_service = IdeaService(db_session)
    idea = idea_service.create_idea("Test Idea", "A test idea description")

    # Add research question
    research_service = ResearchService(db_session)
    question = research_service.add_research_question(
        idea.id, "What is the total addressable market size?"
    )

    assert question.id is not None
    assert question.idea_id == idea.id
    assert question.question == "What is the total addressable market size?"
    assert question.status == "PENDING"
    assert question.created_at is not None


def test_mark_question_answered(db_session: Session):
    """Test marking a research question as answered."""
    # Create an idea and question
    idea_service = IdeaService(db_session)
    idea = idea_service.create_idea("Test Idea", "A test idea description")

    research_service = ResearchService(db_session)
    question = research_service.add_research_question(idea.id, "Test question?")
    assert question.status == "PENDING"

    # Mark as answered
    updated_question = research_service.mark_question_answered(question.id)
    assert updated_question.status == "ANSWERED"


def test_get_questions_for_idea(db_session: Session):
    """Test retrieving all research questions for an idea."""
    # Create an idea
    idea_service = IdeaService(db_session)
    idea = idea_service.create_idea("Test Idea", "A test idea description")

    # Add multiple questions
    research_service = ResearchService(db_session)
    q1 = research_service.add_research_question(idea.id, "Question 1?")
    q2 = research_service.add_research_question(idea.id, "Question 2?")

    # Retrieve questions
    questions = research_service.get_questions_for_idea(idea.id)

    assert len(questions) == 2
    # Should be ordered by created_at desc (newest first)
    assert questions[0].id == q2.id
    assert questions[1].id == q1.id


def test_add_evidence_for_nonexistent_idea(db_session: Session):
    """Test adding evidence for a non-existent idea raises error."""
    research_service = ResearchService(db_session)

    with pytest.raises(EntityNotFoundError):
        research_service.add_evidence(
            999, "Test Evidence", "https://example.com", EvidenceType.ARTICLE
        )


def test_mark_nonexistent_question_answered(db_session: Session):
    """Test marking a non-existent question as answered raises error."""
    research_service = ResearchService(db_session)

    with pytest.raises(EntityNotFoundError):
        research_service.mark_question_answered(999)