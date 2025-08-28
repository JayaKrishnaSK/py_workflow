"""
Core workflow engine using LangGraph.
"""

from typing import Dict, Any, Optional, List, Callable
from langgraph import StateGraph, END
from langgraph.graph import Graph
from langgraph.checkpoint import MemorySaver
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, AIMessage
import asyncio
import uuid
from datetime import datetime

from app.models.workflow import Workflow, WorkflowNode, NodeType
from app.models.execution import WorkflowExecution, ExecutionStatus, HumanInteraction
from app.models.agent import Agent
from app.core.llm_providers import get_llm
from app.services.agent_service import AgentService
from app.services.tool_service import ToolService


class WorkflowState(Dict[str, Any]):
    """State container for workflow execution."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "messages" not in self:
            self["messages"] = []
        if "variables" not in self:
            self["variables"] = {}
        if "current_node" not in self:
            self["current_node"] = None
        if "execution_id" not in self:
            self["execution_id"] = None


class WorkflowEngine:
    """Core workflow execution engine using LangGraph."""
    
    def __init__(self):
        self.agent_service = AgentService()
        self.tool_service = ToolService()
        self._graphs: Dict[str, Graph] = {}
        self._checkpointer = MemorySaver()
    
    async def build_graph(self, workflow: Workflow) -> Graph:
        """Build LangGraph from workflow definition."""
        # Create state graph
        graph = StateGraph(WorkflowState)
        
        # Add nodes
        for node in workflow.nodes:
            if node.type == NodeType.START:
                graph.add_node("__start__", self._start_node)
            elif node.type == NodeType.END:
                graph.add_node("__end__", self._end_node)
            elif node.type == NodeType.AGENT:
                graph.add_node(node.id, self._create_agent_node(node))
            elif node.type == NodeType.TOOL:
                graph.add_node(node.id, self._create_tool_node(node))
            elif node.type == NodeType.HUMAN:
                graph.add_node(node.id, self._create_human_node(node))
            elif node.type == NodeType.CONDITION:
                graph.add_node(node.id, self._create_condition_node(node))
        
        # Add edges
        for edge in workflow.edges:
            if edge.condition:
                # Conditional edge
                graph.add_conditional_edges(
                    edge.source,
                    self._create_condition_function(edge.condition),
                    {
                        True: edge.target,
                        False: END
                    }
                )
            else:
                # Simple edge
                graph.add_edge(edge.source, edge.target)
        
        # Set entry point
        start_nodes = [node for node in workflow.nodes if node.type == NodeType.START]
        if start_nodes:
            graph.set_entry_point("__start__")
        
        # Compile graph
        compiled_graph = graph.compile(checkpointer=self._checkpointer)
        
        # Cache the graph
        self._graphs[str(workflow.id)] = compiled_graph
        
        return compiled_graph
    
    async def execute_workflow(
        self, 
        workflow: Workflow, 
        execution: WorkflowExecution,
        input_data: Dict[str, Any] = None
    ) -> WorkflowExecution:
        """Execute a workflow."""
        if input_data is None:
            input_data = {}
        
        # Get or build graph
        graph = self._graphs.get(str(workflow.id))
        if not graph:
            graph = await self.build_graph(workflow)
        
        # Initialize state
        initial_state = WorkflowState({
            "input_data": input_data,
            "variables": workflow.variables.copy(),
            "execution_id": str(execution.id),
            "workflow_id": str(workflow.id),
            "messages": []
        })
        
        # Update execution
        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.utcnow()
        execution.input_data = input_data
        execution.add_log("INFO", f"Starting workflow execution: {workflow.name}")
        
        try:
            # Execute graph
            config = RunnableConfig(
                configurable={"thread_id": str(execution.id)}
            )
            
            final_state = await graph.ainvoke(initial_state, config=config)
            
            # Update execution with results
            execution.status = ExecutionStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.output_data = final_state.get("output_data", {})
            execution.add_log("INFO", "Workflow execution completed successfully")
            
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.completed_at = datetime.utcnow()
            execution.error_message = str(e)
            execution.add_log("ERROR", f"Workflow execution failed: {str(e)}")
        
        # Calculate execution time
        if execution.started_at and execution.completed_at:
            execution.execution_time_ms = int(
                (execution.completed_at - execution.started_at).total_seconds() * 1000
            )
        
        return execution
    
    async def resume_workflow(
        self, 
        execution: WorkflowExecution,
        human_response: Dict[str, Any] = None
    ) -> WorkflowExecution:
        """Resume a paused workflow execution."""
        workflow_id = execution.workflow_id
        
        # Get graph
        graph = self._graphs.get(workflow_id)
        if not graph:
            raise ValueError(f"No compiled graph found for workflow {workflow_id}")
        
        # Update execution status
        execution.status = ExecutionStatus.RUNNING
        execution.add_log("INFO", "Resuming workflow execution")
        
        try:
            # Get current state from checkpoint
            config = RunnableConfig(
                configurable={"thread_id": str(execution.id)}
            )
            
            # Add human response to state if provided
            if human_response and execution.pending_interaction_id:
                # Find the pending interaction and update it
                for interaction in execution.human_interactions:
                    if interaction.id == execution.pending_interaction_id:
                        interaction.response = human_response
                        interaction.responded_at = datetime.utcnow()
                        break
                
                execution.pending_interaction_id = None
            
            # Resume execution
            final_state = await graph.ainvoke(None, config=config)
            
            # Update execution
            execution.status = ExecutionStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.output_data = final_state.get("output_data", {})
            execution.add_log("INFO", "Workflow execution resumed and completed")
            
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.completed_at = datetime.utcnow()
            execution.error_message = str(e)
            execution.add_log("ERROR", f"Workflow execution failed on resume: {str(e)}")
        
        return execution
    
    # Node creation methods
    async def _start_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Start node implementation."""
        state["current_node"] = "__start__"
        return state
    
    async def _end_node(self, state: WorkflowState) -> Dict[str, Any]:
        """End node implementation."""
        state["current_node"] = "__end__"
        state["output_data"] = state.get("variables", {})
        return state
    
    def _create_agent_node(self, node: WorkflowNode) -> Callable:
        """Create an agent node function."""
        async def agent_node(state: WorkflowState) -> Dict[str, Any]:
            state["current_node"] = node.id
            
            try:
                # Get agent configuration
                agent_id = node.config.get("agent_id")
                if not agent_id:
                    raise ValueError(f"Agent node {node.id} missing agent_id in config")
                
                # Get agent
                agent = await self.agent_service.get_agent(agent_id)
                if not agent:
                    raise ValueError(f"Agent {agent_id} not found")
                
                # Get LLM
                llm = await get_llm(agent.llm_provider, agent.llm_model, agent.llm_config)
                
                # Get tools
                tools = await self.tool_service.get_tools_for_agent(agent)
                
                # Create agent instance
                agent_instance = await self.agent_service.create_agent_instance(agent, llm, tools)
                
                # Get input from state
                input_message = state.get("input_message", "")
                if not input_message and state.get("messages"):
                    input_message = state["messages"][-1].content if state["messages"] else ""
                
                # Execute agent
                response = await agent_instance.ainvoke({"input": input_message})
                
                # Update state
                state["messages"].append(AIMessage(content=response["output"]))
                state["variables"].update(response.get("variables", {}))
                
                return state
                
            except Exception as e:
                # Log error and continue
                state["error"] = str(e)
                return state
        
        return agent_node
    
    def _create_tool_node(self, node: WorkflowNode) -> Callable:
        """Create a tool node function."""
        async def tool_node(state: WorkflowState) -> Dict[str, Any]:
            state["current_node"] = node.id
            
            try:
                # Get tool configuration
                tool_name = node.config.get("tool_name")
                tool_args = node.config.get("tool_args", {})
                
                if not tool_name:
                    raise ValueError(f"Tool node {node.id} missing tool_name in config")
                
                # Execute tool
                tool_instance = await self.tool_service.get_tool(tool_name)
                result = await tool_instance.ainvoke(tool_args)
                
                # Update state
                state["variables"][f"{node.id}_result"] = result
                
                return state
                
            except Exception as e:
                state["error"] = str(e)
                return state
        
        return tool_node
    
    def _create_human_node(self, node: WorkflowNode) -> Callable:
        """Create a human interaction node function."""
        async def human_node(state: WorkflowState) -> Dict[str, Any]:
            state["current_node"] = node.id
            
            # Create human interaction request
            interaction_id = str(uuid.uuid4())
            prompt = node.config.get("prompt", "Human input required")
            input_schema = node.config.get("input_schema", {})
            
            # This would trigger a pause in the workflow
            # The actual implementation would use LangGraph's interrupt mechanism
            state["human_interaction"] = {
                "id": interaction_id,
                "node_id": node.id,
                "prompt": prompt,
                "input_schema": input_schema,
                "requires_response": True
            }
            
            return state
        
        return human_node
    
    def _create_condition_node(self, node: WorkflowNode) -> Callable:
        """Create a condition node function."""
        async def condition_node(state: WorkflowState) -> Dict[str, Any]:
            state["current_node"] = node.id
            
            # Evaluate condition
            condition = node.config.get("condition", "True")
            
            # Simple condition evaluation (in production, use safer evaluation)
            try:
                result = eval(condition, {"state": state, "variables": state.get("variables", {})})
                state["condition_result"] = bool(result)
            except Exception:
                state["condition_result"] = False
            
            return state
        
        return condition_node
    
    def _create_condition_function(self, condition: str) -> Callable:
        """Create a condition function for conditional edges."""
        def condition_func(state: WorkflowState) -> bool:
            try:
                return bool(eval(condition, {"state": state, "variables": state.get("variables", {})}))
            except Exception:
                return False
        
        return condition_func