import os
from idea_tracker.infrastructure.ai_providers.base import AIProvider
from idea_tracker.infrastructure.ai_providers.ollama import OllamaProvider


def get_ai_provider() -> AIProvider:
    """Get AI provider based on environment configuration."""
    provider_type = os.getenv("LLM_PROVIDER", "ollama").lower()
    model = os.getenv("LLM_MODEL", "llama3.2")

    if provider_type == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return OllamaProvider(base_url=base_url, model=model)
    elif provider_type == "openai":
        raise NotImplementedError("OpenAI provider not yet implemented")
    elif provider_type == "anthropic":
        raise NotImplementedError("Anthropic provider not yet implemented")

    raise ValueError(f"Unsupported AI provider: {provider_type}")
