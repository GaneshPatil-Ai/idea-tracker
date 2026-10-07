"""API routes for ideas."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from idea_tracker.application.services.idea_service import IdeaService
from idea_tracker.infrastructure.persistence.database import get_db
from idea_tracker.domain.models.idea import SourceEnum
from idea_tracker.domain.models.content import Tag

router = APIRouter(prefix="/api", tags=["ideas"])


@router.get("/ideas")
def get_ideas(db: Session = Depends(get_db)) -> dict:
    """Get all ideas."""
    from idea_tracker.domain.models.idea import Idea
    ideas = db.query(Idea).all()
    return {
        "ideas": [
            {
                "id": i.id,
                "title": i.title,
                "description": i.description,
                "status": i.status.value,
                "tags": [t.name for t in i.tags],
                "created_at": i.created_at.isoformat() if i.created_at else None,
            }
            for i in ideas
        ]
    }


@router.post("/ideas")
def create_new_idea(
    data: dict,
    db: Session = Depends(get_db),
) -> dict:
    """Create a new idea."""
    service = IdeaService(db)
    idea = service.create_idea(
        title=data.get("title", ""),
        description=data.get("description", "") or data.get("raw_description", ""),
        source=SourceEnum.MANUAL,
    )
    # Add tags if provided
    tags = data.get("tags", [])
    if tags:
        for tag_name in tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            idea.tags.append(tag)
        db.commit()
    return {
        "id": idea.id,
        "title": idea.title,
        "description": idea.description,
        "status": idea.status.value,
        "tags": tags,
    }
