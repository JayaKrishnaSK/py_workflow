# py_workflow

# Basic Documentation for the Agentic Workflow System

## Overview

This system is a dynamic, JSON-configurable agentic workflow executor built using LangChain and LangGraph. It allows defining workflows as graphs with nodes for agents, tools, human-in-the-loop interactions, and more. The system supports selectable LLM providers (Ollama for local models or Google Gemini via API). Custom agents can use internal Python functions as tools or external tools via the Model Context Protocol (MCP) interface, configured in JSON. Human-in-the-loop is implemented using LangGraph's interrupt mechanisms, where workflows can pause for user input via API endpoints. Memory is handled with MongoDB for persisting chat history and graph states (using LangGraph's checkpointer). Tracing and monitoring are provided by the open-source Arize Phoenix framework. The entire system is exposed via a FastAPI backend for execution, management, and interaction.

Key Features:

- **Dynamic Workflow Building**: Parse JSON to construct LangGraph graphs.

- **LLM Providers**: Select Ollama (local) or Gemini (API-based).

- **Custom Agents & Tools**: Agents with internal functions or MCP external tools.

- **Human-in-the-Loop**: Pauses for human approval/input.

- **Memory**: MongoDB for state persistence.

- **Tracing**: Phoenix for observability.

- **API**: FastAPI for workflow management.
