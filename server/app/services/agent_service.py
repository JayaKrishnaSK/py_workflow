"""
Agent service for managing agents and creating agent instances.
"""

from typing import List, Optional, Dict, Any
from bson import ObjectId
from langchain.agents import AgentExecutor, create_react_agent, create_structured_chat_agent
from langchain.agents.agent_types import AgentType as LangChainAgentType
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory

from app.models.agent import Agent, AgentType, AgentCreateRequest, AgentUpdateRequest


class AgentService:
    """Service for managing agents."""
    
    async def create_agent(self, agent_data: AgentCreateRequest) -> Agent:
        """Create a new agent."""
        agent = Agent(**agent_data.dict())
        await agent.save()
        return agent
    
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID."""
        if not ObjectId.is_valid(agent_id):
            return None
        
        return await Agent.get(ObjectId(agent_id))
    
    async def get_agents(
        self, 
        skip: int = 0, 
        limit: int = 100,
        tags: Optional[List[str]] = None
    ) -> List[Agent]:
        """Get list of agents with pagination."""
        query = Agent.find()
        
        if tags:
            query = query.find({"tags": {"$in": tags}})
        
        return await query.skip(skip).limit(limit).to_list()
    
    async def update_agent(self, agent_id: str, agent_data: AgentUpdateRequest) -> Optional[Agent]:
        """Update an existing agent."""
        agent = await self.get_agent(agent_id)
        if not agent:
            return None
        
        # Update fields
        update_data = agent_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        
        agent.update_timestamp()
        await agent.save()
        return agent
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent."""
        agent = await self.get_agent(agent_id)
        if not agent:
            return False
        
        await agent.delete()
        return True
    
    async def create_agent_instance(
        self, 
        agent: Agent, 
        llm: BaseChatModel, 
        tools: List[BaseTool]
    ) -> AgentExecutor:
        """Create a LangChain agent instance from an Agent model."""
        
        # Create memory if configured
        memory = None
        if agent.memory_config.get("enabled", False):
            memory = ConversationBufferWindowMemory(
                k=agent.memory_config.get("window_size", 10),
                return_messages=True,
                memory_key="chat_history"
            )
        
        # Create prompt
        if agent.type == AgentType.REACT:
            # ReAct agent prompt
            prompt_template = """
You are a helpful assistant. Use the following tools to answer questions.

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}
"""
            
            if agent.system_prompt:
                prompt_template = agent.system_prompt + "\n\n" + prompt_template
            
            prompt = PromptTemplate.from_template(prompt_template)
            
            # Create ReAct agent
            agent_instance = create_react_agent(llm, tools, prompt)
            
        elif agent.type == AgentType.FUNCTION_CALLING:
            # Function calling agent
            prompt_template = """
You are a helpful assistant with access to various tools.
Use the tools to help answer questions and complete tasks.

{system_prompt}

{chat_history}
Human: {input}
Assistant: I'll help you with that. Let me use the appropriate tools if needed.

{agent_scratchpad}
"""
            
            prompt = PromptTemplate.from_template(
                prompt_template.format(
                    system_prompt=agent.system_prompt or "",
                    chat_history="{chat_history}" if memory else "",
                    input="{input}",
                    agent_scratchpad="{agent_scratchpad}"
                )
            )
            
            # Create structured chat agent (which supports function calling)
            agent_instance = create_structured_chat_agent(llm, tools, prompt)
            
        elif agent.type == AgentType.CHAT:
            # Simple chat agent without tools
            from langchain.agents import initialize_agent
            
            agent_instance = initialize_agent(
                tools=tools,
                llm=llm,
                agent=LangChainAgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                memory=memory,
                verbose=True,
                max_iterations=agent.max_iterations
            )
            
            return agent_instance
            
        else:
            # Default to ReAct
            prompt = PromptTemplate.from_template(
                f"""
{agent.system_prompt or "You are a helpful assistant."}

{{tools}}

Use the following format:
Question: {{input}}
Thought: {{agent_scratchpad}}
"""
            )
            agent_instance = create_react_agent(llm, tools, prompt)
        
        # Create agent executor
        executor = AgentExecutor(
            agent=agent_instance,
            tools=tools,
            memory=memory,
            verbose=True,
            max_iterations=agent.max_iterations,
            early_stopping_method="generate",
            handle_parsing_errors=True
        )
        
        return executor
    
    async def test_agent(self, agent_id: str, test_input: str) -> Dict[str, Any]:
        """Test an agent with a given input."""
        from app.core.llm_providers import get_llm
        from app.services.tool_service import ToolService
        
        agent = await self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Get LLM
        llm = await get_llm(agent.llm_provider, agent.llm_model, agent.llm_config)
        
        # Get tools
        tool_service = ToolService()
        tools = await tool_service.get_tools_for_agent(agent)
        
        # Create agent instance
        agent_instance = await self.create_agent_instance(agent, llm, tools)
        
        try:
            # Execute agent
            result = await agent_instance.ainvoke({"input": test_input})
            
            return {
                "success": True,
                "output": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output": None
            }