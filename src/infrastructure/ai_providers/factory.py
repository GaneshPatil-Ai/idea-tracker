from src.infrastructure.ai_providers.base import AIProvider
from src.infrastructure.ai_providers.ollama import OllamaProvider
from src.config import Settings as settings

def get_ai_provider() -> AIProvider:
    config = settings.dict()
    provider_type = config.get("LLM_PROVIDER")

    if provider_type == "ollama":
        return OllamaProvider(
            base_url=config.get("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=config.get("LLM_MODEL", "llama3.2")
        )
    elif provider_type == "openai":
        # TODO: Implement OpenAIProvider
        raise NotImplementedError("OpenAI provider not implemented")
    elif provider_type == "anthropic":
        # TODO: Implement AnthropicProvider
        raise NotImplementedError("Anthropic provider not implemented")

    raise ValueError(f"Unsupported AI provider: {provider_type}")
