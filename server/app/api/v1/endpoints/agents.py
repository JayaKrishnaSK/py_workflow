"""
Agent management endpoints.
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional, Dict, Any

from app.models.agent import (
    Agent,
    AgentCreateRequest,
    AgentUpdateRequest,
    AgentResponse,
    AgentType
)
from app.services.agent_service import AgentService

router = APIRouter()
agent_service = AgentService()


@router.post("/", response_model=AgentResponse)
async def create_agent(agent_data: AgentCreateRequest):
    """Create a new agent."""
    try:
        agent = await agent_service.create_agent(agent_data)
        return AgentResponse(**agent.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[AgentResponse])
async def get_agents(
    skip: int = Query(0, ge=0, description="Number of agents to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of agents to return"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags")
):
    """Get list of agents with pagination and filtering."""
    try:
        agents = await agent_service.get_agents(
            skip=skip,
            limit=limit,
            tags=tags
        )
        return [AgentResponse(**agent.dict()) for agent in agents]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str = Path(..., description="Agent ID")):
    """Get a specific agent by ID."""
    try:
        agent = await agent_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return AgentResponse(**agent.dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_data: AgentUpdateRequest,
    agent_id: str = Path(..., description="Agent ID")
):
    """Update an existing agent."""
    try:
        agent = await agent_service.update_agent(agent_id, agent_data)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return AgentResponse(**agent.dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str = Path(..., description="Agent ID")):
    """Delete an agent."""
    try:
        success = await agent_service.delete_agent(agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {"message": "Agent deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/test")
async def test_agent(
    test_input: str,
    agent_id: str = Path(..., description="Agent ID")
):
    """Test an agent with a given input."""
    try:
        result = await agent_service.test_agent(agent_id, test_input)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types/")
async def get_agent_types():
    """Get available agent types."""
    return {
        "agent_types": [
            {
                "type": agent_type.value,
                "description": f"{agent_type.value.replace('_', ' ').title()} agent"
            }
            for agent_type in AgentType
        ]
    }