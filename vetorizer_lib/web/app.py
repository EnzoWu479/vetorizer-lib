"""FastAPI application factory.

This module creates and configures the FastAPI application instance
with routes, templates, and static files.
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from vetorizer_lib.web.config import get_settings
from vetorizer_lib.web.deps import init_metadata_store
from vetorizer_lib.web.routes import databases, upload, search, config

# Paths for templates and static files
WEB_DIR = Path(__file__).parent
TEMPLATES_DIR = WEB_DIR / "templates"
STATIC_DIR = WEB_DIR / "static"


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.

    Example:
        >>> app = create_app()
        >>> # Run with uvicorn
        >>> import uvicorn
        >>> uvicorn.run(app, host="127.0.0.1", port=8000)
    """
    settings = get_settings()

    app = FastAPI(
        title="Vetorizer Web UI",
        description="Web interface for vector database management, CSV ingestion, and semantic search",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount static files
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # Setup templates
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    app.state.templates = templates

    # Register API routers
    app.include_router(databases.router)
    app.include_router(upload.router)
    app.include_router(search.router)
    app.include_router(config.router)

    # Startup event to initialize metadata store
    @app.on_event("startup")
    def startup_event() -> None:
        """Initialize metadata store on application startup."""
        init_metadata_store()

    # Health check endpoint
    @app.get("/api/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint.

        Returns:
            Dictionary with status "ok".
        """
        return {"status": "ok"}

    # Page routes (render HTML templates)
    @app.get("/", response_class=HTMLResponse)
    async def home_page(request: Request) -> HTMLResponse:
        """Home page with upload form and database list.

        Args:
            request: FastAPI request object.

        Returns:
            Rendered HTML template.
        """
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/search", response_class=HTMLResponse)
    async def search_page(request: Request) -> HTMLResponse:
        """Search page.

        Args:
            request: FastAPI request object.

        Returns:
            Rendered HTML template.
        """
        return templates.TemplateResponse("search.html", {"request": request})

    @app.get("/compare", response_class=HTMLResponse)
    async def compare_page(request: Request) -> HTMLResponse:
        """Comparison page.

        Args:
            request: FastAPI request object.

        Returns:
            Rendered HTML template.
        """
        return templates.TemplateResponse("compare.html", {"request": request})

    @app.get("/manage", response_class=HTMLResponse)
    async def manage_page(request: Request) -> HTMLResponse:
        """Database management page.

        Args:
            request: FastAPI request object.

        Returns:
            Rendered HTML template.
        """
        return templates.TemplateResponse("manage.html", {"request": request})

    return app


# Create default app instance for uvicorn
app = create_app()
