#!/bin/bash

# Agentic Workflow System - Quick Start Script

set -e

echo "🚀 Starting Agentic Workflow System Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "server" ] || [ ! -d "client" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Setting up Agentic Workflow System..."

# Check dependencies
print_status "Checking dependencies..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is required but not installed"
    exit 1
fi

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm is required but not installed"
    exit 1
fi

print_success "Dependencies check passed"

# Setup backend
print_status "Setting up backend..."
cd server

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file..."
    cp .env.example .env
    print_success ".env file created from template"
else
    print_warning ".env file already exists"
fi

# Try to install basic Python dependencies
print_status "Installing basic Python dependencies..."
if pip3 install fastapi uvicorn python-dotenv pydantic &> /dev/null; then
    print_success "Basic Python dependencies installed"
else
    print_warning "Could not install Python dependencies. Please install manually:"
    echo "  pip3 install fastapi uvicorn python-dotenv pydantic"
fi

cd ..

# Setup frontend
print_status "Setting up frontend..."
cd client

if [ ! -d "node_modules" ]; then
    print_status "Installing Node.js dependencies..."
    if npm install &> /dev/null; then
        print_success "Node.js dependencies installed"
    else
        print_error "Failed to install Node.js dependencies"
        exit 1
    fi
else
    print_warning "Node.js dependencies already installed"
fi

cd ..

# Check if Docker is available for MongoDB
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    print_status "Docker detected. You can start MongoDB with:"
    echo "  docker-compose up -d mongodb"
else
    print_warning "Docker not detected. You'll need to install MongoDB manually"
fi

# Final instructions
echo ""
print_success "Setup complete! 🎉"
echo ""
echo "To start the system:"
echo ""
echo "1. Start the backend server:"
echo "   cd server"
echo "   python test_server.py  # Simple server"
echo "   # OR (with full dependencies):"
echo "   # python main.py"
echo ""
echo "2. In another terminal, start the frontend:"
echo "   cd client"
echo "   npm run dev"
echo ""
echo "3. Optional: Start MongoDB (if you have Docker):"
echo "   docker-compose up -d mongodb"
echo ""
echo "URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs (with full server)"
echo ""
print_status "Happy workflow building! 🤖"