# Agentic Workflow Client

React frontend for the Agentic Workflow System.

## Features

- **Modern React UI**: Built with React 18 and Vite
- **Responsive Design**: Tailwind CSS v4 with mobile-first approach
- **Workflow Management**: Create, edit, and manage workflows
- **Execution Monitoring**: Real-time execution tracking and logs
- **Agent Configuration**: Set up and test AI agents
- **Tools & Providers**: Manage LLM providers and tools

## Tech Stack

- **React 18**: Modern React with hooks
- **Vite**: Fast development and build tool
- **Tailwind CSS v4**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls
- **Heroicons**: Beautiful SVG icons

## Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

## Development

The client is configured to proxy API requests to the backend server running on `http://localhost:8000`.

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Lint code
- `npm run lint:fix` - Fix linting issues

### Project Structure

```
src/
├── components/          # Reusable UI components
│   └── Layout.jsx      # Main layout component
├── pages/              # Page components
│   ├── Dashboard.jsx   # Dashboard overview
│   ├── Workflows.jsx   # Workflow management
│   ├── Executions.jsx  # Execution monitoring
│   ├── Agents.jsx      # Agent configuration
│   └── Tools.jsx       # Tools and providers
├── services/           # API services
│   └── api.js         # Axios API client
├── utils/             # Utility functions
├── hooks/             # Custom React hooks
├── App.jsx            # Main app component
├── main.jsx           # React entry point
└── index.css          # Global styles
```

## API Integration

The client communicates with the backend API through Axios. All API calls are centralized in `src/services/api.js`.

### API Endpoints

- **Health**: System health checks
- **Workflows**: CRUD operations for workflows
- **Executions**: Workflow execution management
- **Agents**: AI agent configuration
- **Tools**: Available tools and LLM providers

## Styling

The app uses Tailwind CSS v4 with custom utility classes for workflow-specific components:

- `.workflow-node` - Workflow node styling
- `.workflow-edge` - Workflow edge styling
- `.status-*` - Status badge variants

## Features Overview

### Dashboard
- System health status
- Quick statistics
- Recent executions

### Workflows
- List all workflows
- Create/edit workflows
- Visual workflow builder (planned)
- Workflow validation and testing

### Executions
- Monitor workflow executions
- View execution logs
- Human-in-the-loop interactions

### Agents
- Configure AI agents
- Set up LLM providers
- Test agent responses

### Tools
- Browse available tools
- Manage LLM providers
- View tool configurations

## Planned Features

- **Visual Workflow Builder**: Drag-and-drop workflow editor
- **Real-time Updates**: WebSocket integration for live execution updates
- **Advanced Monitoring**: Detailed execution analytics and metrics
- **User Management**: Authentication and user roles
- **Workflow Templates**: Pre-built workflow templates
- **Export/Import**: Workflow sharing and backup