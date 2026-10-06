"""Health check routes."""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from idea_tracker.config.settings import settings
from idea_tracker.infrastructure.persistence.database import get_db

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Health check endpoint.

    Verifies database connectivity and returns application status.
    """
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {e!s}"

    return {
        "status": "ok" if db_status == "healthy" else "degraded",
        "app_name": settings.app_name,
        "environment": settings.app_env.value,
        "database": db_status,
        "version": "0.1.0",
    }
