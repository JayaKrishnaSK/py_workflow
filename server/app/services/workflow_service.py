"""
Workflow service for managing workflows and executions.
"""

from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime

from app.models.workflow import (
    Workflow, 
    WorkflowCreateRequest, 
    WorkflowUpdateRequest,
    WorkflowStatus
)
from app.models.execution import (
    WorkflowExecution,
    ExecutionCreateRequest,
    ExecutionStatus,
    HumanInteraction,
    HumanInteractionResponse
)
from app.core.workflow_engine import WorkflowEngine


class WorkflowService:
    """Service for managing workflows and executions."""
    
    def __init__(self):
        self.workflow_engine = WorkflowEngine()
    
    # Workflow Management
    async def create_workflow(self, workflow_data: WorkflowCreateRequest) -> Workflow:
        """Create a new workflow."""
        workflow = Workflow(**workflow_data.dict())
        await workflow.save()
        return workflow
    
    async def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID."""
        if not ObjectId.is_valid(workflow_id):
            return None
        
        return await Workflow.get(ObjectId(workflow_id))
    
    async def get_workflows(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[WorkflowStatus] = None,
        tags: Optional[List[str]] = None
    ) -> List[Workflow]:
        """Get list of workflows with pagination and filtering."""
        query = Workflow.find()
        
        if status:
            query = query.find({"status": status})
        
        if tags:
            query = query.find({"tags": {"$in": tags}})
        
        return await query.skip(skip).limit(limit).to_list()
    
    async def update_workflow(
        self, 
        workflow_id: str, 
        workflow_data: WorkflowUpdateRequest
    ) -> Optional[Workflow]:
        """Update an existing workflow."""
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            return None
        
        # Update fields
        update_data = workflow_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(workflow, field, value)
        
        workflow.update_timestamp()
        await workflow.save()
        return workflow
    
    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            return False
        
        # Check if there are active executions
        active_executions = await WorkflowExecution.find(
            {
                "workflow_id": workflow_id,
                "status": {"$in": [ExecutionStatus.RUNNING, ExecutionStatus.PAUSED, ExecutionStatus.WAITING_FOR_HUMAN]}
            }
        ).to_list()
        
        if active_executions:
            raise ValueError("Cannot delete workflow with active executions")
        
        await workflow.delete()
        return True
    
    async def duplicate_workflow(self, workflow_id: str, new_name: str) -> Optional[Workflow]:
        """Duplicate an existing workflow."""
        original = await self.get_workflow(workflow_id)
        if not original:
            return None
        
        # Create duplicate
        duplicate_data = original.dict(exclude={"id", "created_at", "updated_at"})
        duplicate_data["name"] = new_name
        duplicate_data["status"] = WorkflowStatus.DRAFT
        
        duplicate = Workflow(**duplicate_data)
        await duplicate.save()
        return duplicate
    
    # Execution Management
    async def create_execution(self, execution_data: ExecutionCreateRequest) -> WorkflowExecution:
        """Create a new workflow execution."""
        # Verify workflow exists
        workflow = await self.get_workflow(execution_data.workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {execution_data.workflow_id} not found")
        
        if workflow.status != WorkflowStatus.ACTIVE:
            raise ValueError(f"Cannot execute workflow with status {workflow.status}")
        
        # Create execution
        execution = WorkflowExecution(
            workflow_id=execution_data.workflow_id,
            workflow_version=workflow.version,
            input_data=execution_data.input_data,
            status=ExecutionStatus.PENDING
        )
        
        await execution.save()
        return execution
    
    async def start_execution(self, execution_id: str) -> WorkflowExecution:
        """Start a workflow execution."""
        execution = await self.get_execution(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
        
        if execution.status != ExecutionStatus.PENDING:
            raise ValueError(f"Cannot start execution with status {execution.status}")
        
        # Get workflow
        workflow = await self.get_workflow(execution.workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {execution.workflow_id} not found")
        
        # Execute workflow
        execution = await self.workflow_engine.execute_workflow(
            workflow, execution, execution.input_data
        )
        
        await execution.save()
        return execution
    
    async def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get execution by ID."""
        if not ObjectId.is_valid(execution_id):
            return None
        
        return await WorkflowExecution.get(ObjectId(execution_id))
    
    async def get_executions(
        self,
        workflow_id: Optional[str] = None,
        status: Optional[ExecutionStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[WorkflowExecution]:
        """Get list of executions with filtering."""
        query = WorkflowExecution.find()
        
        if workflow_id:
            query = query.find({"workflow_id": workflow_id})
        
        if status:
            query = query.find({"status": status})
        
        return await query.skip(skip).limit(limit).to_list()
    
    async def cancel_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Cancel a workflow execution."""
        execution = await self.get_execution(execution_id)
        if not execution:
            return None
        
        if execution.status not in [ExecutionStatus.RUNNING, ExecutionStatus.PAUSED, ExecutionStatus.WAITING_FOR_HUMAN]:
            raise ValueError(f"Cannot cancel execution with status {execution.status}")
        
        execution.status = ExecutionStatus.CANCELLED
        execution.completed_at = datetime.utcnow()
        execution.add_log("INFO", "Execution cancelled by user")
        
        await execution.save()
        return execution
    
    # Human-in-the-Loop
    async def get_pending_interactions(self, execution_id: str) -> List[HumanInteraction]:
        """Get pending human interactions for an execution."""
        execution = await self.get_execution(execution_id)
        if not execution:
            return []
        
        # Return interactions that haven't been responded to
        return [
            interaction for interaction in execution.human_interactions
            if interaction.response is None
        ]
    
    async def respond_to_interaction(
        self,
        execution_id: str,
        interaction_id: str,
        response: HumanInteractionResponse
    ) -> Optional[WorkflowExecution]:
        """Respond to a human interaction and resume workflow."""
        execution = await self.get_execution(execution_id)
        if not execution:
            return None
        
        # Find the interaction
        interaction = None
        for inter in execution.human_interactions:
            if inter.id == interaction_id:
                interaction = inter
                break
        
        if not interaction:
            raise ValueError(f"Interaction {interaction_id} not found")
        
        if interaction.response is not None:
            raise ValueError(f"Interaction {interaction_id} already responded to")
        
        # Update interaction
        interaction.response = response.response
        interaction.responded_at = datetime.utcnow()
        
        # Clear pending interaction
        if execution.pending_interaction_id == interaction_id:
            execution.pending_interaction_id = None
        
        # Resume workflow
        execution = await self.workflow_engine.resume_workflow(execution, response.response)
        
        await execution.save()
        return execution
    
    # Validation and Testing
    async def validate_workflow(self, workflow: Workflow) -> Dict[str, Any]:
        """Validate a workflow configuration."""
        errors = []
        warnings = []
        
        # Check for start and end nodes
        start_nodes = [node for node in workflow.nodes if node.type.value == "start"]
        end_nodes = [node for node in workflow.nodes if node.type.value == "end"]
        
        if not start_nodes:
            errors.append("Workflow must have at least one start node")
        
        if not end_nodes:
            warnings.append("Workflow should have at least one end node")
        
        # Check for orphaned nodes
        node_ids = {node.id for node in workflow.nodes}
        connected_nodes = set()
        
        for edge in workflow.edges:
            connected_nodes.add(edge.source)
            connected_nodes.add(edge.target)
        
        orphaned_nodes = node_ids - connected_nodes
        if orphaned_nodes:
            warnings.append(f"Orphaned nodes found: {list(orphaned_nodes)}")
        
        # Check for cycles (basic check)
        # In a production system, implement proper cycle detection
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    async def test_workflow(
        self, 
        workflow_id: str, 
        test_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test a workflow with sample input."""
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # Create a test execution
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            workflow_version=workflow.version,
            input_data=test_input,
            status=ExecutionStatus.PENDING
        )
        
        try:
            # Execute workflow
            execution = await self.workflow_engine.execute_workflow(
                workflow, execution, test_input
            )
            
            return {
                "success": execution.status == ExecutionStatus.COMPLETED,
                "status": execution.status,
                "output_data": execution.output_data,
                "error_message": execution.error_message,
                "execution_time_ms": execution.execution_time_ms,
                "logs": [log.dict() for log in execution.logs]
            }
            
        except Exception as e:
            return {
                "success": False,
                "status": "failed",
                "error_message": str(e),
                "output_data": None,
                "execution_time_ms": None,
                "logs": []
            }