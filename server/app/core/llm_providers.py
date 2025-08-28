"""
LLM provider implementations for Ollama and Google Gemini.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel

from app.core.config import settings


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def get_llm(self, model: str, config: Dict[str, Any]) -> BaseChatModel:
        """Get LLM instance with specified model and configuration."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Get list of available models."""
        pass


class OllamaProvider(LLMProvider):
    """Ollama LLM provider implementation."""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
    
    async def get_llm(self, model: str, config: Dict[str, Any]) -> BaseChatModel:
        """Get Ollama LLM instance."""
        llm_config = {
            "model": model,
            "base_url": self.base_url,
            "temperature": config.get("temperature", 0.7),
            "top_p": config.get("top_p", 0.9),
            "top_k": config.get("top_k", 40),
            "repeat_penalty": config.get("repeat_penalty", 1.1),
            "num_ctx": config.get("num_ctx", 4096),
            **config
        }
        
        return ChatOllama(**llm_config)
    
    def get_available_models(self) -> list[str]:
        """Get available Ollama models."""
        # In a real implementation, you would query the Ollama API
        return [
            "llama2",
            "llama2:13b",
            "llama2:70b",
            "mistral",
            "codellama",
            "vicuna",
            "alpaca"
        ]


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider implementation."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GOOGLE_API_KEY
        if not self.api_key:
            raise ValueError("Google API key is required for Gemini provider")
    
    async def get_llm(self, model: str, config: Dict[str, Any]) -> BaseChatModel:
        """Get Gemini LLM instance."""
        llm_config = {
            "model": model,
            "google_api_key": self.api_key,
            "temperature": config.get("temperature", 0.7),
            "top_p": config.get("top_p", 0.9),
            "top_k": config.get("top_k", 40),
            "max_output_tokens": config.get("max_output_tokens", 2048),
            **config
        }
        
        return ChatGoogleGenerativeAI(**llm_config)
    
    def get_available_models(self) -> list[str]:
        """Get available Gemini models."""
        return [
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ]


class LLMProviderFactory:
    """Factory for creating LLM providers."""
    
    _providers = {
        "ollama": OllamaProvider,
        "gemini": GeminiProvider
    }
    
    @classmethod
    def create_provider(cls, provider_name: str, **kwargs) -> LLMProvider:
        """Create LLM provider instance."""
        if provider_name not in cls._providers:
            raise ValueError(f"Unknown LLM provider: {provider_name}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(**kwargs)
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available providers."""
        return list(cls._providers.keys())


# Global provider instances
_provider_cache: Dict[str, LLMProvider] = {}


async def get_llm_provider(provider_name: str) -> LLMProvider:
    """Get or create LLM provider instance."""
    if provider_name not in _provider_cache:
        _provider_cache[provider_name] = LLMProviderFactory.create_provider(provider_name)
    
    return _provider_cache[provider_name]


async def get_llm(provider_name: str, model: str, config: Dict[str, Any] = None) -> BaseChatModel:
    """Get LLM instance from specified provider."""
    if config is None:
        config = {}
    
    provider = await get_llm_provider(provider_name)
    return await provider.get_llm(model, config)