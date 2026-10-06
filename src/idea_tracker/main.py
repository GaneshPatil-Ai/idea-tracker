"""Main FastAPI application factory and entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from idea_tracker.config.logging import configure_logging, get_logger
from idea_tracker.config.settings import settings
from idea_tracker.domain.exceptions import IdeaTrackerError
from idea_tracker.infrastructure.persistence.database import init_db
from idea_tracker.web.routes.health import router as health_router
from idea_tracker.web.routes.reviews import router as reviews_router
from idea_tracker.web.routes.research import router as research_router
from idea_tracker.web.routes.search import router as search_router
from idea_tracker.web.routes.export import router as export_router
from idea_tracker.web.routes.ui import router as ui_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown events."""
    configure_logging()
    logger.info("Starting application", app_name=settings.app_name, env=settings.app_env.value)

    # Initialize DB schema for development/testing
    if settings.is_testing or settings.app_env.value == "development":
        init_db()

    yield

    logger.info("Shutting down application")


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Local-first idea capture → execution system.",
        lifespan=lifespan,
    )

    # Global Exception Handlers
    @app.exception_handler(IdeaTrackerError)
    async def domain_exception_handler(request: Request, exc: IdeaTrackerError) -> JSONResponse:
        logger.warning("Domain exception occurred", error=str(exc), path=request.url.path)
        return JSONResponse(
            status_code=400,
            content={"error": exc.__class__.__name__, "message": exc.message},
        )

    # Register Routers
    app.include_router(health_router, tags=["System"])
    app.include_router(reviews_router)
    app.include_router(research_router)
    app.include_router(search_router)
    app.include_router(export_router)
    app.include_router(ui_router)

    return app


app = create_app()


def cli_main() -> None:
    """CLI entry point for running the uvicorn server."""
    import uvicorn

    uvicorn.run(
        "idea_tracker.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.app_env.value == "development",
    )


if __name__ == "__main__":
    cli_main()
