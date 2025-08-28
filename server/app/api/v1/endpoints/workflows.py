"""
Workflow management endpoints.
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional, Dict, Any
from bson import ObjectId

from app.models.workflow import (
    Workflow,
    WorkflowCreateRequest,
    WorkflowUpdateRequest,
    WorkflowResponse,
    WorkflowStatus
)
from app.services.workflow_service import WorkflowService

router = APIRouter()
workflow_service = WorkflowService()


@router.post("/", response_model=WorkflowResponse)
async def create_workflow(workflow_data: WorkflowCreateRequest):
    """Create a new workflow."""
    try:
        workflow = await workflow_service.create_workflow(workflow_data)
        return WorkflowResponse(**workflow.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[WorkflowResponse])
async def get_workflows(
    skip: int = Query(0, ge=0, description="Number of workflows to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of workflows to return"),
    status: Optional[WorkflowStatus] = Query(None, description="Filter by workflow status"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags")
):
    """Get list of workflows with pagination and filtering."""
    try:
        workflows = await workflow_service.get_workflows(
            skip=skip,
            limit=limit,
            status=status,
            tags=tags
        )
        return [WorkflowResponse(**workflow.dict()) for workflow in workflows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str = Path(..., description="Workflow ID")):
    """Get a specific workflow by ID."""
    try:
        workflow = await workflow_service.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return WorkflowResponse(**workflow.dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_data: WorkflowUpdateRequest,
    workflow_id: str = Path(..., description="Workflow ID")
):
    """Update an existing workflow."""
    try:
        workflow = await workflow_service.update_workflow(workflow_id, workflow_data)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return WorkflowResponse(**workflow.dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str = Path(..., description="Workflow ID")):
    """Delete a workflow."""
    try:
        success = await workflow_service.delete_workflow(workflow_id)
        if not success:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {"message": "Workflow deleted successfully"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{workflow_id}/duplicate", response_model=WorkflowResponse)
async def duplicate_workflow(
    new_name: str,
    workflow_id: str = Path(..., description="Workflow ID")
):
    """Duplicate an existing workflow."""
    try:
        workflow = await workflow_service.duplicate_workflow(workflow_id, new_name)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return WorkflowResponse(**workflow.dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{workflow_id}/validate")
async def validate_workflow(workflow_id: str = Path(..., description="Workflow ID")):
    """Validate a workflow configuration."""
    try:
        workflow = await workflow_service.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        validation_result = await workflow_service.validate_workflow(workflow)
        return validation_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{workflow_id}/test")
async def test_workflow(
    test_input: Dict[str, Any],
    workflow_id: str = Path(..., description="Workflow ID")
):
    """Test a workflow with sample input."""
    try:
        result = await workflow_service.test_workflow(workflow_id, test_input)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))