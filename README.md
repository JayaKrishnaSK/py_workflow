# Agentic Workflow System

A comprehensive, dynamic JSON-configurable agentic workflow executor built with LangChain, LangGraph, FastAPI, and React.

## Overview

This system allows you to define workflows as graphs with nodes for agents, tools, human-in-the-loop interactions, and more. It supports selectable LLM providers (Ollama for local models or Google Gemini via API), custom agents with internal Python functions or external tools via the Model Context Protocol (MCP), and persistent memory with MongoDB.

## Key Features

- **Dynamic Workflow Building**: Parse JSON to construct LangGraph graphs
- **LLM Providers**: Select Ollama (local) or Gemini (API-based)
- **Custom Agents & Tools**: Agents with internal functions or MCP external tools
- **Human-in-the-Loop**: Pauses for human approval/input
- **Memory**: MongoDB for state persistence
- **Tracing**: Phoenix for observability
- **API**: FastAPI for workflow management
- **Modern UI**: React frontend with Tailwind CSS

## Architecture

This is a monorepo with:
- `server/` - Python FastAPI backend
- `client/` - React frontend with Vite and Tailwind CSS v4

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB (optional, for full functionality)
- Ollama (optional, for local LLM support)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd py_workflow
```

2. **Backend Setup**
```bash
cd server
pip install fastapi uvicorn python-dotenv
cp .env.example .env
# Edit .env with your configuration
```

3. **Frontend Setup**
```bash
cd ../client
npm install
```

### Running the System

1. **Start the Backend**
```bash
cd server
python test_server.py  # Simple server for testing
# OR (with full dependencies installed):
# python main.py
```
The API will be available at http://localhost:8000

2. **Start the Frontend**
```bash
cd client
npm run dev
```
The UI will be available at http://localhost:3000

### API Documentation

With the backend running, visit:
- Swagger UI: http://localhost:8000/docs (when using full FastAPI server)
- API Health: http://localhost:8000/health

## Project Structure

```
py_workflow/
├── server/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core functionality
│   │   ├── models/        # Data models
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utilities
│   ├── main.py           # FastAPI application
│   ├── requirements.txt  # Python dependencies
│   └── .env.example      # Environment configuration
├── client/                # React frontend
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API client
│   │   └── utils/        # Utilities
│   ├── package.json      # Node dependencies
│   └── vite.config.js    # Vite configuration
└── README.md             # This file
```

## Features Implemented

### Backend
- ✅ FastAPI server with full REST API
- ✅ Comprehensive data models (Workflow, Execution, Agent)
- ✅ LangGraph integration for workflow execution
- ✅ LLM provider abstractions (Ollama, Gemini)
- ✅ Tool system with internal functions and MCP support
- ✅ MongoDB integration with async operations
- ✅ Health monitoring and system status
- ✅ Human-in-the-loop workflow interrupts

### Frontend
- ✅ Modern React 18 application with Vite
- ✅ Responsive UI with Tailwind CSS v4
- ✅ Navigation with React Router
- ✅ Dashboard with system overview
- ✅ Workflow management interface
- ✅ Execution monitoring (basic)
- ✅ API integration with Axios
- ✅ Error handling and loading states

## API Endpoints

### Core Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /health/detailed` - Detailed system status

### Workflows
- `POST /api/v1/workflows/` - Create workflow
- `GET /api/v1/workflows/` - List workflows
- `GET /api/v1/workflows/{id}` - Get workflow details
- `PUT /api/v1/workflows/{id}` - Update workflow
- `DELETE /api/v1/workflows/{id}` - Delete workflow

### Executions
- `POST /api/v1/executions/` - Create execution
- `POST /api/v1/executions/{id}/start` - Start execution
- `GET /api/v1/executions/` - List executions
- `GET /api/v1/executions/{id}` - Get execution details

### Agents
- `POST /api/v1/agents/` - Create agent
- `GET /api/v1/agents/` - List agents
- `GET /api/v1/agents/{id}` - Get agent details

### Tools
- `GET /api/v1/tools/` - List available tools
- `GET /api/v1/tools/providers/` - List LLM providers

## Configuration

### Environment Variables

Create a `.env` file in the server directory:

```env
# LLM Configuration
DEFAULT_LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
GOOGLE_API_KEY=your-api-key-here

# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=agentic_workflow

# Tracing
ENABLE_TRACING=true
```

## Development

### Backend Development
```bash
cd server
pip install -r requirements.txt
python main.py
```

### Frontend Development
```bash
cd client
npm run dev
```

### Testing
```bash
# Backend tests (when available)
cd server && pytest

# Frontend tests (when available)
cd client && npm test
```

## Next Steps

1. **Full Dependency Installation**: Install all Python dependencies for complete functionality
2. **Database Setup**: Configure MongoDB for persistent storage
3. **LLM Provider Setup**: Configure Ollama or Google Gemini
4. **Visual Workflow Builder**: Implement drag-and-drop workflow creation
5. **Real-time Updates**: Add WebSocket support for live execution monitoring
6. **User Authentication**: Add user management and permissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test your changes
5. Submit a pull request

## License

MIT License - see LICENSE file for details
