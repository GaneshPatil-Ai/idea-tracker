"""API routes for data export."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from idea_tracker.application.services.export_service import ExportService
from idea_tracker.infrastructure.persistence.database import get_db

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/ideas")
def export_all_ideas(
    format: str = "json",
    db: Session = Depends(get_db),
) -> Response:
    """Export all ideas in specified format.

    Args:
        format: 'json' or 'markdown'

    Returns:
        Exported data as file or JSON response
    """
    if format not in ["json", "markdown"]:
        raise HTTPException(400, "Format must be 'json' or 'markdown'")

    service = ExportService(db)
    data = service.export_all_ideas(format)

    if format == "json":
        return Response(content=data, media_type="application/json")
    else:
        return Response(content=data, media_type="text/markdown")


@router.get("/ideas/{idea_id}")
def export_idea(
    idea_id: int,
    format: str = "json",
    db: Session = Depends(get_db),
) -> Response:
    """Export single idea with all related content.

    Args:
        idea_id: Idea to export
        format: 'json' or 'markdown'

    Returns:
        Exported data as file or JSON response
    """
    if format not in ["json", "markdown"]:
        raise HTTPException(400, "Format must be 'json' or 'markdown'")

    service = ExportService(db)
    try:
        data = service.export_idea(idea_id, format)
    except ValueError as e:
        raise HTTPException(404, str(e)) from None

    if format == "json":
        return Response(content=data, media_type="application/json")
    else:
        return Response(content=data, media_type="text/markdown")
