"""
Workflow execution data models.
"""

from beanie import Document
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class ExecutionStatus(str, Enum):
    """Execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_FOR_HUMAN = "waiting_for_human"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionNodeStatus(str, Enum):
    """Individual node execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ExecutionLog(BaseModel):
    """Log entry for workflow execution."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str = Field(..., description="Log level (INFO, WARNING, ERROR)")
    message: str = Field(..., description="Log message")
    node_id: Optional[str] = Field(None, description="Node ID if applicable")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional log data")


class NodeExecution(BaseModel):
    """Execution state for a single node."""
    node_id: str = Field(..., description="Node ID")
    status: ExecutionNodeStatus = Field(default=ExecutionNodeStatus.PENDING)
    started_at: Optional[datetime] = Field(None)
    completed_at: Optional[datetime] = Field(None)
    input_data: Optional[Dict[str, Any]] = Field(None)
    output_data: Optional[Dict[str, Any]] = Field(None)
    error_message: Optional[str] = Field(None)
    execution_time_ms: Optional[int] = Field(None)


class HumanInteraction(BaseModel):
    """Human interaction request."""
    id: str = Field(..., description="Unique interaction ID")
    node_id: str = Field(..., description="Node requesting interaction")
    prompt: str = Field(..., description="Prompt for human")
    input_schema: Optional[Dict[str, Any]] = Field(None, description="Expected input schema")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = Field(None)
    response: Optional[Dict[str, Any]] = Field(None)
    timeout_at: Optional[datetime] = Field(None)


class WorkflowExecution(Document):
    """Workflow execution document model."""
    
    workflow_id: str = Field(..., description="Reference to workflow")
    workflow_version: str = Field(..., description="Workflow version at execution time")
    status: ExecutionStatus = Field(default=ExecutionStatus.PENDING)
    
    # Execution data
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Initial input data")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Final output data")
    current_node_id: Optional[str] = Field(None, description="Currently executing node")
    
    # Node execution tracking
    node_executions: List[NodeExecution] = Field(default_factory=list)
    
    # Human interactions
    human_interactions: List[HumanInteraction] = Field(default_factory=list)
    pending_interaction_id: Optional[str] = Field(None, description="Currently pending interaction")
    
    # Execution metadata
    started_at: Optional[datetime] = Field(None)
    completed_at: Optional[datetime] = Field(None)
    error_message: Optional[str] = Field(None)
    execution_time_ms: Optional[int] = Field(None)
    
    # Logging
    logs: List[ExecutionLog] = Field(default_factory=list)
    
    # Graph state (for LangGraph checkpointing)
    graph_state: Optional[Dict[str, Any]] = Field(None)
    checkpoint_id: Optional[str] = Field(None)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="User who started execution")
    
    class Settings:
        collection = "workflow_executions"

    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

    def add_log(self, level: str, message: str, node_id: Optional[str] = None, data: Optional[Dict[str, Any]] = None):
        """Add a log entry."""
        log_entry = ExecutionLog(
            level=level,
            message=message,
            node_id=node_id,
            data=data
        )
        self.logs.append(log_entry)
        self.update_timestamp()

    def get_node_execution(self, node_id: str) -> Optional[NodeExecution]:
        """Get execution state for a specific node."""
        for node_exec in self.node_executions:
            if node_exec.node_id == node_id:
                return node_exec
        return None

    def update_node_execution(self, node_id: str, **updates):
        """Update execution state for a specific node."""
        node_exec = self.get_node_execution(node_id)
        if node_exec:
            for key, value in updates.items():
                if hasattr(node_exec, key):
                    setattr(node_exec, key, value)
        else:
            # Create new node execution
            node_exec = NodeExecution(node_id=node_id, **updates)
            self.node_executions.append(node_exec)
        self.update_timestamp()


class ExecutionCreateRequest(BaseModel):
    """Request model for creating a workflow execution."""
    workflow_id: str
    input_data: Dict[str, Any] = Field(default_factory=dict)


class ExecutionResponse(BaseModel):
    """Response model for execution operations."""
    id: str
    workflow_id: str
    workflow_version: str
    status: ExecutionStatus
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    current_node_id: Optional[str]
    node_executions: List[NodeExecution]
    human_interactions: List[HumanInteraction]
    pending_interaction_id: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    execution_time_ms: Optional[int]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]


class HumanInteractionResponse(BaseModel):
    """Response model for human interaction."""
    response: Dict[str, Any]