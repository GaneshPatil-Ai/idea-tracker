"""API routes for research evidence and questions."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from idea_tracker.application.services.research_service import ResearchService
from idea_tracker.domain.models.research import EvidenceType
from idea_tracker.infrastructure.persistence.database import get_db

router = APIRouter(prefix="/ideas", tags=["research"])


# Evidence endpoints
@router.post("/{idea_id}/evidence")
def add_evidence(
    idea_id: int,
    title: str,
    url: str,
    evidence_type: str,
    author: Optional[str] = None,
    publication_date: Optional[str] = None,
    summary: Optional[str] = None,
    db: Session = Depends(get_db),
) -> dict:
    """Add research evidence to an idea."""
    try:
        type_enum = EvidenceType(evidence_type)
    except ValueError:
        raise HTTPException(
            400, f"Invalid evidence type. Must be one of: {[e.value for e in EvidenceType]}"
        ) from None

    pub_date = None
    if publication_date:
        try:
            pub_date = datetime.fromisoformat(publication_date)
        except ValueError:
            raise HTTPException(400, "Invalid publication_date format. Use ISO format.") from None

    service = ResearchService(db)
    evidence = service.add_evidence(idea_id, title, url, type_enum, author, pub_date, summary)
    return {
        "id": evidence.id,
        "idea_id": evidence.idea_id,
        "title": evidence.title,
        "url": evidence.url,
        "evidence_type": evidence.evidence_type.value,
        "created_at": evidence.created_at.isoformat(),
    }


@router.get("/{idea_id}/evidence")
def get_evidence(idea_id: int, db: Session = Depends(get_db)) -> dict:
    """Get all research evidence for an idea."""
    service = ResearchService(db)
    evidence_list = service.get_evidence_for_idea(idea_id)
    return {
        "idea_id": idea_id,
        "evidence": [
            {
                "id": e.id,
                "title": e.title,
                "url": e.url,
                "evidence_type": e.evidence_type.value,
                "author": e.author,
                "publication_date": e.publication_date.isoformat() if e.publication_date else None,
                "summary": e.summary,
                "created_at": e.created_at.isoformat(),
            }
            for e in evidence_list
        ],
    }


# Research question endpoints
@router.post("/{idea_id}/research-questions")
def add_research_question(
    idea_id: int,
    question: str,
    db: Session = Depends(get_db),
) -> dict:
    """Add a research question to an idea."""
    service = ResearchService(db)
    q = service.add_research_question(idea_id, question)
    return {
        "id": q.id,
        "idea_id": q.idea_id,
        "question": q.question,
        "status": q.status,
        "created_at": q.created_at.isoformat(),
    }


@router.post("/research-questions/{question_id}/mark-answered")
def mark_question_answered(question_id: int, db: Session = Depends(get_db)) -> dict:
    """Mark a research question as answered."""
    service = ResearchService(db)
    q = service.mark_question_answered(question_id)
    return {
        "id": q.id,
        "idea_id": q.idea_id,
        "status": q.status,
    }


@router.get("/{idea_id}/research-questions")
def get_research_questions(idea_id: int, db: Session = Depends(get_db)) -> dict:
    """Get all research questions for an idea."""
    service = ResearchService(db)
    questions = service.get_questions_for_idea(idea_id)
    return {
        "idea_id": idea_id,
        "questions": [
            {
                "id": q.id,
                "question": q.question,
                "status": q.status,
                "created_at": q.created_at.isoformat(),
            }
            for q in questions
        ],
    }
