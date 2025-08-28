"""
Workflow execution endpoints.
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional, Dict, Any

from app.models.execution import (
    WorkflowExecution,
    ExecutionCreateRequest,
    ExecutionResponse,
    ExecutionStatus,
    HumanInteraction,
    HumanInteractionResponse
)
from app.services.workflow_service import WorkflowService

router = APIRouter()
workflow_service = WorkflowService()


@router.post("/", response_model=ExecutionResponse)
async def create_execution(execution_data: ExecutionCreateRequest):
    """Create a new workflow execution."""
    try:
        execution = await workflow_service.create_execution(execution_data)
        return ExecutionResponse(**execution.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{execution_id}/start", response_model=ExecutionResponse)
async def start_execution(execution_id: str = Path(..., description="Execution ID")):
    """Start a workflow execution."""
    try:
        execution = await workflow_service.start_execution(execution_id)
        return ExecutionResponse(**execution.dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ExecutionResponse])
async def get_executions(
    workflow_id: Optional[str] = Query(None, description="Filter by workflow ID"),
    status: Optional[ExecutionStatus] = Query(None, description="Filter by execution status"),
    skip: int = Query(0, ge=0, description="Number of executions to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of executions to return")
):
    """Get list of executions with filtering."""
    try:
        executions = await workflow_service.get_executions(
            workflow_id=workflow_id,
            status=status,
            skip=skip,
            limit=limit
        )
        return [ExecutionResponse(**execution.dict()) for execution in executions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(execution_id: str = Path(..., description="Execution ID")):
    """Get a specific execution by ID."""
    try:
        execution = await workflow_service.get_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        return ExecutionResponse(**execution.dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{execution_id}/cancel", response_model=ExecutionResponse)
async def cancel_execution(execution_id: str = Path(..., description="Execution ID")):
    """Cancel a workflow execution."""
    try:
        execution = await workflow_service.cancel_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        return ExecutionResponse(**execution.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{execution_id}/interactions", response_model=List[HumanInteraction])
async def get_pending_interactions(execution_id: str = Path(..., description="Execution ID")):
    """Get pending human interactions for an execution."""
    try:
        interactions = await workflow_service.get_pending_interactions(execution_id)
        return interactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{execution_id}/interactions/{interaction_id}/respond", response_model=ExecutionResponse)
async def respond_to_interaction(
    response: HumanInteractionResponse,
    execution_id: str = Path(..., description="Execution ID"),
    interaction_id: str = Path(..., description="Interaction ID")
):
    """Respond to a human interaction and resume workflow."""
    try:
        execution = await workflow_service.respond_to_interaction(
            execution_id, interaction_id, response
        )
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        return ExecutionResponse(**execution.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{execution_id}/logs")
async def get_execution_logs(execution_id: str = Path(..., description="Execution ID")):
    """Get execution logs."""
    try:
        execution = await workflow_service.get_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        return {
            "execution_id": execution_id,
            "logs": [log.dict() for log in execution.logs]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{execution_id}/status")
async def get_execution_status(execution_id: str = Path(..., description="Execution ID")):
    """Get execution status summary."""
    try:
        execution = await workflow_service.get_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        return {
            "execution_id": execution_id,
            "status": execution.status,
            "current_node_id": execution.current_node_id,
            "started_at": execution.started_at,
            "completed_at": execution.completed_at,
            "execution_time_ms": execution.execution_time_ms,
            "pending_interaction_id": execution.pending_interaction_id,
            "node_executions": [
                {
                    "node_id": node_exec.node_id,
                    "status": node_exec.status,
                    "execution_time_ms": node_exec.execution_time_ms
                }
                for node_exec in execution.node_executions
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))