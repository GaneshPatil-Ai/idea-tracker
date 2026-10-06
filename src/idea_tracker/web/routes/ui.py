"""Web routes for serving HTML templates and UI endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from idea_tracker.application.services.idea_service import IdeaService
from idea_tracker.infrastructure.persistence.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    """Main dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/ideas/{idea_id}", response_class=HTMLResponse)
def idea_detail(request: Request, idea_id: int):
    """Idea detail page."""
    return templates.TemplateResponse("detail.html", {"request": request, "idea_id": idea_id})


# API endpoints for the UI
@router.get("/api/ideas")
def list_ideas(db: Session = Depends(get_db)):
    """Get all ideas for the dashboard."""
    ideas = db.query(Idea).order_by(Idea.updated_at.desc()).all()
    return [
        {
            "id": idea.id,
            "title": idea.title,
            "raw_description": idea.raw_description,
            "status": idea.status.value,
            "tags": [tag.name for tag in idea.tags],
            "created_at": idea.created_at.isoformat(),
            "updated_at": idea.updated_at.isoformat(),
        }
        for idea in ideas
    ]


@router.post("/api/ideas")
def create_idea(
    data: dict,
    db: Session = Depends(get_db)
):
    """Create a new idea."""
    service = IdeaService(db)
    idea = service.create_idea(
        title=data["title"],
        raw_description=data["raw_description"]
    )

    # Add tags if provided
    if data.get("tags"):
        from idea_tracker.domain.models.content import Tag
        for tag_name in data["tags"]:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            idea.tags.append(tag)
        db.commit()

    return {"id": idea.id, "status": "created"}


@router.get("/api/ideas/{idea_id}")
def get_idea(idea_id: int, db: Session = Depends(get_db)):
    """Get idea details."""
    from idea_tracker.domain.models.idea import Idea
    idea = db.get(Idea, idea_id)
    if not idea:
        raise HTTPException(404, "Idea not found")

    return {
        "id": idea.id,
        "title": idea.title,
        "raw_description": idea.raw_description,
        "structured_description": idea.structured_description,
        "status": idea.status.value,
        "tags": [tag.name for tag in idea.tags],
        "created_at": idea.created_at.isoformat(),
        "updated_at": idea.updated_at.isoformat(),
    }


@router.put("/api/ideas/{idea_id}/status")
def update_status(
    idea_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Update idea status."""
    service = IdeaService(db)
    from idea_tracker.domain.models.idea import StatusEnum

    try:
        status = StatusEnum(data["status"])
        idea = service.update_status(idea_id, status)
        return {"id": idea.id, "status": idea.status.value}
    except ValueError:
        raise HTTPException(400, f"Invalid status: {data['status']}")


@router.get("/api/ideas/{idea_id}/milestones")
def get_milestones(idea_id: int, db: Session = Depends(get_db)):
    """Get milestones for an idea."""
    from idea_tracker.domain.models.execution import Milestone
    milestones = db.query(Milestone).filter(Milestone.idea_id == idea_id).all()

    return {
        "milestones": [
            {
                "id": m.id,
                "title": m.title,
                "status": m.status,
                "created_at": m.created_at.isoformat(),
            }
            for m in milestones
        ]
    }


@router.post("/api/ideas/{idea_id}/milestones")
def create_milestone(
    idea_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Create a milestone for an idea."""
    from idea_tracker.application.services.execution_service import ExecutionService
    service = ExecutionService(db)
    milestone = service.create_milestone(idea_id, data["title"], data.get("description"))
    return {"id": milestone.id, "status": "created"}