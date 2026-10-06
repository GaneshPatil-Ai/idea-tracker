"""API routes for search functionality."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from idea_tracker.application.services.search_service import SearchService
from idea_tracker.infrastructure.persistence.database import get_db

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/ideas")
def search_ideas(
    q: str = Query(..., description="Search query", min_length=1),
    search_type: str = Query("hybrid", description="Search type: keyword, full_text, or hybrid"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> dict:
    """Search ideas using keyword or full-text search."""
    if search_type not in ["keyword", "full_text", "hybrid"]:
        raise HTTPException(400, "Invalid search_type. Must be: keyword, full_text, or hybrid")

    service = SearchService(db)
    try:
        return service.search_ideas(q, search_type, limit, offset)
    except ValueError as e:
        raise HTTPException(400, str(e)) from None


@router.get("/ideas/by-tag/{tag_name}")
def search_by_tag(
    tag_name: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> dict:
    """Search ideas by tag."""
    service = SearchService(db)
    return service.search_by_tag(tag_name, limit, offset)


@router.get("/ideas/by-status/{status}")
def search_by_status(
    status: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> dict:
    """Search ideas by status."""
    service = SearchService(db)
    return service.search_by_status(status, limit, offset)


@router.get("/decisions/by-outcome/{outcome}")
def search_decisions_by_outcome(
    outcome: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    """Search decisions by outcome."""
    service = SearchService(db)
    return service.search_decisions_by_outcome(outcome, limit)


@router.get("/ideas/{idea_id}/related")
def get_related_ideas(
    idea_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """Get related ideas based on shared tags."""
    service = SearchService(db)
    return service.get_related_ideas(idea_id)
