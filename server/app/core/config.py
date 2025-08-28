"""
Application configuration using Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    """
    
    # Application
    APP_NAME: str = "Agentic Workflow System"
    DEBUG: bool = False
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "agentic_workflow"
    
    # LLM Configuration
    DEFAULT_LLM_PROVIDER: str = "ollama"  # or "gemini"
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    
    # Google Gemini Configuration
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-pro"
    
    # LangSmith Configuration (optional)
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "agentic-workflow"
    
    # Phoenix Tracing
    ENABLE_TRACING: bool = True
    PHOENIX_PORT: int = 6006
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # MCP Configuration
    MCP_SERVERS: dict = {}
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()