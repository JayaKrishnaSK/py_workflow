"""
Main FastAPI application for the Agentic Workflow System.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.core.database import init_database
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Async context manager for application lifespan events.
    """
    # Startup
    await init_database()
    print("✅ Database initialized")
    
    # Initialize Phoenix tracing if enabled
    if settings.ENABLE_TRACING:
        try:
            import phoenix as px
            px.launch_app()
            print("✅ Phoenix tracing initialized")
        except ImportError:
            print("⚠️  Phoenix not available, tracing disabled")
    
    yield
    
    # Shutdown
    print("🔴 Application shutdown")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title="Agentic Workflow System",
        description="Dynamic, JSON-configurable agentic workflow executor using LangChain and LangGraph",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/")
    async def root():
        """Root endpoint with basic information."""
        return {
            "message": "Agentic Workflow System API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/api/v1/health"
        }

    @app.get("/health")
    async def health_check():
        """Simple health check endpoint."""
        return {"status": "healthy", "version": "1.0.0"}

    return app


# Create the application instance
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )