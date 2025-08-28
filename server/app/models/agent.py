"""
Agent data models.
"""

from beanie import Document
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    """Types of agents."""
    CHAT = "chat"
    FUNCTION_CALLING = "function_calling"
    REACT = "react"
    PLAN_AND_EXECUTE = "plan_and_execute"
    CUSTOM = "custom"


class ToolType(str, Enum):
    """Types of tools."""
    INTERNAL = "internal"  # Python function
    MCP = "mcp"  # Model Context Protocol
    LANGCHAIN = "langchain"  # LangChain tool


class Tool(BaseModel):
    """Tool definition."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    type: ToolType = Field(..., description="Tool type")
    config: Dict[str, Any] = Field(default_factory=dict, description="Tool configuration")
    
    # For internal tools
    function_name: Optional[str] = Field(None, description="Python function name")
    module_path: Optional[str] = Field(None, description="Python module path")
    
    # For MCP tools
    server_name: Optional[str] = Field(None, description="MCP server name")
    
    # Schema information
    input_schema: Optional[Dict[str, Any]] = Field(None, description="Input schema")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="Output schema")


class Agent(Document):
    """Agent document model."""
    
    name: str = Field(..., description="Agent name")
    description: Optional[str] = Field(None, description="Agent description")
    type: AgentType = Field(..., description="Agent type")
    
    # LLM Configuration
    llm_provider: str = Field(default="ollama", description="LLM provider (ollama/gemini)")
    llm_model: str = Field(default="llama2", description="LLM model name")
    llm_config: Dict[str, Any] = Field(default_factory=dict, description="LLM configuration")
    
    # Agent Configuration
    system_prompt: Optional[str] = Field(None, description="System prompt")
    instructions: Optional[str] = Field(None, description="Agent instructions")
    max_iterations: int = Field(default=10, description="Max iterations for ReAct agents")
    temperature: float = Field(default=0.7, description="LLM temperature")
    
    # Tools
    tools: List[Tool] = Field(default_factory=list, description="Available tools")
    
    # Memory and context
    memory_config: Dict[str, Any] = Field(default_factory=dict, description="Memory configuration")
    context_window: int = Field(default=4000, description="Context window size")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="Creator user ID")
    tags: List[str] = Field(default_factory=list, description="Agent tags")
    
    class Settings:
        collection = "agents"

    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()


class AgentCreateRequest(BaseModel):
    """Request model for creating an agent."""
    name: str
    description: Optional[str] = None
    type: AgentType
    llm_provider: str = "ollama"
    llm_model: str = "llama2"
    llm_config: Dict[str, Any] = Field(default_factory=dict)
    system_prompt: Optional[str] = None
    instructions: Optional[str] = None
    max_iterations: int = 10
    temperature: float = 0.7
    tools: List[Tool] = Field(default_factory=list)
    memory_config: Dict[str, Any] = Field(default_factory=dict)
    context_window: int = 4000
    tags: List[str] = Field(default_factory=list)


class AgentUpdateRequest(BaseModel):
    """Request model for updating an agent."""
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[AgentType] = None
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    llm_config: Optional[Dict[str, Any]] = None
    system_prompt: Optional[str] = None
    instructions: Optional[str] = None
    max_iterations: Optional[int] = None
    temperature: Optional[float] = None
    tools: Optional[List[Tool]] = None
    memory_config: Optional[Dict[str, Any]] = None
    context_window: Optional[int] = None
    tags: Optional[List[str]] = None


class AgentResponse(BaseModel):
    """Response model for agent operations."""
    id: str
    name: str
    description: Optional[str]
    type: AgentType
    llm_provider: str
    llm_model: str
    llm_config: Dict[str, Any]
    system_prompt: Optional[str]
    instructions: Optional[str]
    max_iterations: int
    temperature: float
    tools: List[Tool]
    memory_config: Dict[str, Any]
    context_window: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    tags: List[str]