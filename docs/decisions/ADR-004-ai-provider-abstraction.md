# ADR-004: AI Provider Abstraction

## Status
Accepted

## Context
The application leverages Large Language Models (LLMs) to structure raw ideas, suggest execution steps, and analyze evidence. Users have different preferences for AI providers:
- Privacy-conscious users prefer local models via Ollama.
- Developers may prefer API providers like OpenAI or Anthropic.
- Costs, rate limits, and model capabilities vary across providers.

Hardcoding the application to a single LLM provider would violate the local-first principle and vendor independence.

## Decision
We define a strict **LLM Provider Interface** (`LLMProvider` protocol) in the application layer.

Infrastructure adapters implement this protocol for specific backends:
1. **OllamaAdapter:** Connects to local Ollama instances (offline/local-first).
2. **OpenAIAdapter:** Connects to OpenAI-compatible chat completion endpoints.
3. **AnthropicAdapter:** Connects to Anthropic's Messages API.

The LLM provider is selected strictly via environment configuration (`LLM_PROVIDER=ollama|openai|anthropic|none`).

All AI workflows require LLM responses to be validated against **Pydantic schemas** before persisting.

## Consequences

### Positive
- **Vendor independence:** Users can switch providers by changing an environment variable.
- **Offline operation:** Ollama support ensures full AI capabilities work completely offline.
- **Type safety:** Pydantic validation guarantees raw LLM text is converted into typed objects or rejected.
- **Testability:** Workflows can be tested with mock providers without calling real LLM APIs.

### Negative
- Structured output support varies by provider and model; prompt engineering must accommodate different model capabilities.
- Maintaining multiple provider adapters adds small maintenance surface.
