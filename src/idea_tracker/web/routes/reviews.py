"""API routes for reviews and decisions."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from idea_tracker.infrastructure.persistence.database import get_db
from idea_tracker.application.services.decision_service import DecisionService
from idea_tracker.application.services.review_service import ReviewService
from idea_tracker.domain.models.decision import DecisionOutcome

router = APIRouter(prefix="/ideas", tags=["reviews"])


# Decision endpoints
@router.post("/{idea_id}/decisions")
def create_decision(
    idea_id: int,
    title: str,
    outcome: str,
    rationale: str,
    db: Session = Depends(get_db),
) -> dict:
    """Record a formal decision for an idea."""
    try:
        outcome_enum = DecisionOutcome(outcome)
    except ValueError:
        raise HTTPException(400, f"Invalid outcome. Must be one of: {[e.value for e in DecisionOutcome]}")

    service = DecisionService(db)
    decision = service.create_decision(idea_id, title, outcome_enum, rationale)
    return {
        "id": decision.id,
        "idea_id": decision.idea_id,
        "title": decision.title,
        "outcome": decision.outcome.value,
        "created_at": decision.created_at.isoformat(),
    }


@router.get("/{idea_id}/decisions")
def get_decisions(idea_id: int, db: Session = Depends(get_db)) -> dict:
    """Get all decisions for an idea."""
    service = DecisionService(db)
    decisions = service.get_decisions_for_idea(idea_id)
    return {
        "idea_id": idea_id,
        "decisions": [
            {
                "id": d.id,
                "title": d.title,
                "outcome": d.outcome.value,
                "created_at": d.created_at.isoformat(),
            }
            for d in decisions
        ],
    }


# Review endpoints
@router.post("/{idea_id}/mark-reviewed")
def mark_reviewed(idea_id: int, db: Session = Depends(get_db)) -> dict:
    """Mark an idea as reviewed."""
    service = ReviewService(db)
    idea = service.mark_idea_reviewed(idea_id)
    return {
        "idea_id": idea.id,
        "last_reviewed_at": idea.last_reviewed_at.isoformat() if idea.last_reviewed_at else None,
    }


@router.get("/stale")
def get_stale_ideas(db: Session = Depends(get_db)) -> dict:
    """Get all stale ideas that need review."""
    service = ReviewService(db)
    stale = service.get_stale_ideas()
    return {
        "stale_count": len(stale),
        "ideas": [
            {
                "id": idea.id,
                "title": idea.title,
                "status": idea.status.value,
                "last_reviewed_at": idea.last_reviewed_at.isoformat() if idea.last_reviewed_at else None,
            }
            for idea in stale
        ],
    }
