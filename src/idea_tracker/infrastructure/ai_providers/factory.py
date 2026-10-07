from idea_tracker.infrastructure.ai_providers.base import AIProvider
from idea_tracker.infrastructure.ai_providers.ollama import OllamaProvider
from idea_tracker.config.settings import settings


def get_ai_provider() -> AIProvider:
    """Get AI provider based on settings configuration."""
    provider_type = settings.llm_provider.value.lower()
    model = settings.llm_model

    if provider_type == "ollama":
        base_url = settings.ollama_base_url
        return OllamaProvider(base_url=base_url, model=model)
    elif provider_type == "openai":
        raise NotImplementedError("OpenAI provider not yet implemented")
    elif provider_type == "anthropic":
        raise NotImplementedError("Anthropic provider not yet implemented")

    raise ValueError(f"Unsupported AI provider: {provider_type}")
