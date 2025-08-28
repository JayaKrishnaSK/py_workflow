"""
Workflow data models.
"""

from beanie import Document
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class NodeType(str, Enum):
    """Types of nodes in a workflow."""
    AGENT = "agent"
    TOOL = "tool"
    HUMAN = "human"
    CONDITION = "condition"
    START = "start"
    END = "end"


class WorkflowNode(BaseModel):
    """A node in the workflow graph."""
    id: str = Field(..., description="Unique identifier for the node")
    type: NodeType = Field(..., description="Type of the node")
    name: str = Field(..., description="Human-readable name")
    description: Optional[str] = Field(None, description="Node description")
    config: Dict[str, Any] = Field(default_factory=dict, description="Node configuration")
    position: Optional[Dict[str, float]] = Field(None, description="UI position (x, y)")


class WorkflowEdge(BaseModel):
    """An edge connecting two nodes in the workflow."""
    id: str = Field(..., description="Unique identifier for the edge")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    condition: Optional[str] = Field(None, description="Condition for traversing this edge")
    label: Optional[str] = Field(None, description="Edge label")


class WorkflowStatus(str, Enum):
    """Workflow status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class Workflow(Document):
    """Workflow document model."""
    
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    version: str = Field(default="1.0.0", description="Workflow version")
    status: WorkflowStatus = Field(default=WorkflowStatus.DRAFT, description="Workflow status")
    
    # Graph structure
    nodes: List[WorkflowNode] = Field(default_factory=list, description="Workflow nodes")
    edges: List[WorkflowEdge] = Field(default_factory=list, description="Workflow edges")
    
    # Configuration
    config: Dict[str, Any] = Field(default_factory=dict, description="Global workflow config")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Workflow variables")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="Creator user ID")
    tags: List[str] = Field(default_factory=list, description="Workflow tags")
    
    class Settings:
        collection = "workflows"

    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()


class WorkflowCreateRequest(BaseModel):
    """Request model for creating a workflow."""
    name: str
    description: Optional[str] = None
    nodes: List[WorkflowNode] = Field(default_factory=list)
    edges: List[WorkflowEdge] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)
    variables: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class WorkflowUpdateRequest(BaseModel):
    """Request model for updating a workflow."""
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    status: Optional[WorkflowStatus] = None
    nodes: Optional[List[WorkflowNode]] = None
    edges: Optional[List[WorkflowEdge]] = None
    config: Optional[Dict[str, Any]] = None
    variables: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class WorkflowResponse(BaseModel):
    """Response model for workflow operations."""
    id: str
    name: str
    description: Optional[str]
    version: str
    status: WorkflowStatus
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    config: Dict[str, Any]
    variables: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    tags: List[str]