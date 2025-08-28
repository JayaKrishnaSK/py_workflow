"""
Health check endpoints.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
from datetime import datetime

from app.core.database import get_database
from app.core.config import settings

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "agentic-workflow-system"
    }


@router.get("/detailed")
async def detailed_health_check(db=Depends(get_database)) -> Dict[str, Any]:
    """Detailed health check including database connectivity."""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "agentic-workflow-system",
        "components": {}
    }
    
    # Check database connectivity
    try:
        # Simple database ping
        await db.command("ping")
        health_data["components"]["database"] = {
            "status": "healthy",
            "connection": "active"
        }
    except Exception as e:
        health_data["status"] = "unhealthy"
        health_data["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check LLM providers
    health_data["components"]["llm_providers"] = {
        "default": settings.DEFAULT_LLM_PROVIDER,
        "available": ["ollama", "gemini"]
    }
    
    # Check tracing
    health_data["components"]["tracing"] = {
        "enabled": settings.ENABLE_TRACING,
        "phoenix_port": settings.PHOENIX_PORT if settings.ENABLE_TRACING else None
    }
    
    return health_data