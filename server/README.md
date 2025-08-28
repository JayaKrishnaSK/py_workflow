# Agentic Workflow Server

FastAPI backend for the Agentic Workflow System.

## Features

- **Dynamic Workflow Building**: Parse JSON to construct LangGraph graphs
- **LLM Providers**: Ollama (local) and Google Gemini (API-based)
- **Custom Agents & Tools**: Internal functions and MCP external tools
- **Human-in-the-Loop**: Pause workflows for human input
- **Memory**: MongoDB for state persistence
- **Tracing**: Arize Phoenix for observability

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start MongoDB (if using locally):
```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or install MongoDB locally
```

4. Start Ollama (if using Ollama provider):
```bash
# Install Ollama: https://ollama.ai/
ollama pull llama2
```

## Running the Server

```bash
# Development
python main.py

# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Health
- `GET /health/` - Basic health check
- `GET /health/detailed` - Detailed health check

### Workflows
- `POST /api/v1/workflows/` - Create workflow
- `GET /api/v1/workflows/` - List workflows
- `GET /api/v1/workflows/{id}` - Get workflow
- `PUT /api/v1/workflows/{id}` - Update workflow
- `DELETE /api/v1/workflows/{id}` - Delete workflow
- `POST /api/v1/workflows/{id}/validate` - Validate workflow
- `POST /api/v1/workflows/{id}/test` - Test workflow

### Executions
- `POST /api/v1/executions/` - Create execution
- `POST /api/v1/executions/{id}/start` - Start execution
- `GET /api/v1/executions/` - List executions
- `GET /api/v1/executions/{id}` - Get execution
- `POST /api/v1/executions/{id}/cancel` - Cancel execution
- `GET /api/v1/executions/{id}/interactions` - Get pending interactions
- `POST /api/v1/executions/{id}/interactions/{interaction_id}/respond` - Respond to interaction

### Agents
- `POST /api/v1/agents/` - Create agent
- `GET /api/v1/agents/` - List agents
- `GET /api/v1/agents/{id}` - Get agent
- `PUT /api/v1/agents/{id}` - Update agent
- `DELETE /api/v1/agents/{id}` - Delete agent
- `POST /api/v1/agents/{id}/test` - Test agent

### Tools
- `GET /api/v1/tools/` - List available tools
- `GET /api/v1/tools/{name}` - Get tool info
- `GET /api/v1/tools/providers/` - List LLM providers
- `GET /api/v1/tools/providers/{provider}/models` - Get provider models

## Configuration

Key environment variables:

- `MONGODB_URL`: MongoDB connection string
- `DEFAULT_LLM_PROVIDER`: Either "ollama" or "gemini"
- `OLLAMA_BASE_URL`: Ollama server URL
- `GOOGLE_API_KEY`: Google API key for Gemini
- `ENABLE_TRACING`: Enable Phoenix tracing

## Development

Run tests:
```bash
pytest
```

Code formatting:
```bash
black app/
isort app/
```

Linting:
```bash
flake8 app/
```