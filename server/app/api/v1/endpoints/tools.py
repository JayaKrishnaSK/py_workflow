"""
Tool management endpoints.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional

from app.services.tool_service import ToolService
from app.core.llm_providers import LLMProviderFactory

router = APIRouter()
tool_service = ToolService()


@router.get("/")
async def get_available_tools():
    """Get list of available tools."""
    try:
        tools = tool_service.get_available_tools()
        tool_details = []
        
        for tool_name in tools:
            tool_info = tool_service.get_tool_info(tool_name)
            if tool_info:
                tool_details.append(tool_info)
        
        return {
            "tools": tool_details,
            "count": len(tool_details)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{tool_name}")
async def get_tool_info(tool_name: str):
    """Get information about a specific tool."""
    try:
        tool_info = tool_service.get_tool_info(tool_name)
        if not tool_info:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        return tool_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers/")
async def get_llm_providers():
    """Get available LLM providers."""
    try:
        providers = LLMProviderFactory.get_available_providers()
        
        provider_details = []
        for provider_name in providers:
            try:
                provider = LLMProviderFactory.create_provider(provider_name)
                models = provider.get_available_models()
                provider_details.append({
                    "name": provider_name,
                    "models": models
                })
            except Exception as e:
                provider_details.append({
                    "name": provider_name,
                    "models": [],
                    "error": str(e)
                })
        
        return {
            "providers": provider_details
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers/{provider_name}/models")
async def get_provider_models(provider_name: str):
    """Get available models for a specific provider."""
    try:
        provider = LLMProviderFactory.create_provider(provider_name)
        models = provider.get_available_models()
        
        return {
            "provider": provider_name,
            "models": models
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))