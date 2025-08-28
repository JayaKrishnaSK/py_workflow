"""
Tool service for managing and executing tools.
"""

import importlib
from typing import List, Dict, Any, Optional, Callable
from langchain_core.tools import BaseTool, tool
from langchain.tools import DuckDuckGoSearchRun
from pydantic import BaseModel

from app.models.agent import Agent, Tool, ToolType


class InternalTool(BaseTool):
    """Wrapper for internal Python function tools."""
    
    name: str
    description: str
    function: Callable
    
    def _run(self, *args, **kwargs) -> str:
        """Execute the tool synchronously."""
        try:
            result = self.function(*args, **kwargs)
            return str(result)
        except Exception as e:
            return f"Error executing tool: {str(e)}"
    
    async def _arun(self, *args, **kwargs) -> str:
        """Execute the tool asynchronously."""
        return self._run(*args, **kwargs)


class MCPTool(BaseTool):
    """Wrapper for Model Context Protocol tools."""
    
    name: str
    description: str
    server_name: str
    tool_config: Dict[str, Any]
    
    def _run(self, *args, **kwargs) -> str:
        """Execute the MCP tool synchronously."""
        # In a real implementation, this would communicate with MCP servers
        # For now, return a placeholder
        return f"MCP tool {self.name} executed with args: {args}, kwargs: {kwargs}"
    
    async def _arun(self, *args, **kwargs) -> str:
        """Execute the MCP tool asynchronously."""
        return self._run(*args, **kwargs)


class ToolService:
    """Service for managing and creating tool instances."""
    
    def __init__(self):
        self._tool_cache: Dict[str, BaseTool] = {}
        self._internal_functions: Dict[str, Callable] = {}
        self._register_built_in_tools()
        self._register_internal_functions()
    
    def _register_built_in_tools(self):
        """Register built-in tools."""
        # Example built-in tools
        self._tool_cache["search"] = DuckDuckGoSearchRun()
    
    def _register_internal_functions(self):
        """Register internal Python functions as tools."""
        
        @tool
        def calculator(expression: str) -> str:
            """
            Calculate the result of a mathematical expression.
            
            Args:
                expression: A mathematical expression to evaluate (e.g., "2 + 2", "sqrt(16)")
            
            Returns:
                The result of the calculation
            """
            try:
                # Safe evaluation for basic math
                import math
                
                # Replace common functions
                expression = expression.replace("sqrt", "math.sqrt")
                expression = expression.replace("sin", "math.sin")
                expression = expression.replace("cos", "math.cos")
                expression = expression.replace("tan", "math.tan")
                expression = expression.replace("log", "math.log")
                expression = expression.replace("exp", "math.exp")
                
                # Evaluate safely
                result = eval(expression, {"__builtins__": {}, "math": math})
                return str(result)
            except Exception as e:
                return f"Error: {str(e)}"
        
        @tool
        def text_processor(text: str, operation: str) -> str:
            """
            Process text with various operations.
            
            Args:
                text: The text to process
                operation: The operation to perform (upper, lower, reverse, count_words, count_chars)
            
            Returns:
                The processed text or count
            """
            try:
                if operation == "upper":
                    return text.upper()
                elif operation == "lower":
                    return text.lower()
                elif operation == "reverse":
                    return text[::-1]
                elif operation == "count_words":
                    return str(len(text.split()))
                elif operation == "count_chars":
                    return str(len(text))
                else:
                    return f"Unknown operation: {operation}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        @tool
        def file_reader(file_path: str) -> str:
            """
            Read content from a file.
            
            Args:
                file_path: Path to the file to read
            
            Returns:
                File content or error message
            """
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file: {str(e)}"
        
        # Register tools
        self._tool_cache["calculator"] = calculator
        self._tool_cache["text_processor"] = text_processor
        self._tool_cache["file_reader"] = file_reader
    
    async def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tool_cache.get(tool_name)
    
    async def get_tools_for_agent(self, agent: Agent) -> List[BaseTool]:
        """Get all tools configured for an agent."""
        tools = []
        
        for tool_config in agent.tools:
            tool_instance = await self._create_tool_instance(tool_config)
            if tool_instance:
                tools.append(tool_instance)
        
        return tools
    
    async def _create_tool_instance(self, tool_config: Tool) -> Optional[BaseTool]:
        """Create a tool instance from configuration."""
        
        if tool_config.type == ToolType.INTERNAL:
            # Internal Python function tool
            if tool_config.function_name in self._tool_cache:
                return self._tool_cache[tool_config.function_name]
            
            # Try to load from module
            if tool_config.module_path and tool_config.function_name:
                try:
                    module = importlib.import_module(tool_config.module_path)
                    function = getattr(module, tool_config.function_name)
                    
                    tool_instance = InternalTool(
                        name=tool_config.name,
                        description=tool_config.description,
                        function=function
                    )
                    
                    # Cache the tool
                    self._tool_cache[tool_config.name] = tool_instance
                    return tool_instance
                    
                except Exception as e:
                    print(f"Error loading internal tool {tool_config.name}: {e}")
                    return None
        
        elif tool_config.type == ToolType.MCP:
            # Model Context Protocol tool
            tool_instance = MCPTool(
                name=tool_config.name,
                description=tool_config.description,
                server_name=tool_config.server_name or "",
                tool_config=tool_config.config
            )
            
            return tool_instance
        
        elif tool_config.type == ToolType.LANGCHAIN:
            # LangChain built-in tool
            return self._tool_cache.get(tool_config.name)
        
        return None
    
    def register_tool(self, name: str, tool: BaseTool):
        """Register a custom tool."""
        self._tool_cache[name] = tool
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return list(self._tool_cache.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        tool = self._tool_cache.get(tool_name)
        if not tool:
            return None
        
        return {
            "name": tool.name,
            "description": tool.description,
            "args_schema": tool.args_schema.schema() if tool.args_schema else None
        }