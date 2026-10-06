# AI Architecture

## Principles

1. **AI assists reasoning; it does not make decisions.** Every AI output is a recommendation until the user accepts it.
2. **Structured output only.** LLM responses are validated through Pydantic schemas before persistence.
3. **Provider-agnostic.** The application works with Ollama, OpenAI, Anthropic, or any compatible API.
4. **Graceful degradation.** AI features are optional; all core functionality works without an LLM.
5. **Traceable.** Every AI action produces an activity event.

## Request Flow

```
FastAPI Route
    │
    ▼
Application Service (e.g., IdeaService.structure_idea)
    │
    ▼
AI Workflow (e.g., IdeaStructuringWorkflow)
    │  - Builds prompt from templates
    │  - Defines expected output schema
    │
    ▼
LLM Gateway
    │  - Routes to configured provider
    │  - Handles retries and timeouts
    │
    ▼
LLM Provider (Ollama / OpenAI / Anthropic adapter)
    │
    ▼
Raw LLM Response
    │
    ▼
Pydantic Validation
    │  - Parse and validate structure
    │  - Reject or repair malformed output
    │
    ▼
Persist + Activity Event
```

**Anti-pattern — never do this:**

```python
@app.post("/ideas")
async def create_idea():
    response = openai.chat.completions.create(...)  # NO
```

## LLM Provider Interface

```python
class LLMProvider(Protocol):
    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        response_model: type[BaseModel] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> LLMResponse: ...
```

```python
@dataclass
class LLMResponse:
    content: str
    parsed: BaseModel | None  # Populated when response_model is provided
    model: str
    provider: str
    usage: TokenUsage | None
    duration_ms: int
```

### Provider Adapters

```
infrastructure/llm/
├── base.py           # LLMProvider protocol, LLMResponse, exceptions
├── ollama.py         # Ollama adapter (local models)
├── openai_compat.py  # OpenAI-compatible API adapter
└── anthropic.py      # Anthropic API adapter
```

Each adapter:
- Implements `LLMProvider`
- Handles provider-specific authentication
- Translates to/from provider-specific formats
- Maps provider errors to application-level exceptions

### Configuration

```
LLM_PROVIDER=ollama          # ollama | openai | anthropic
LLM_MODEL=llama3.2           # Model name for the provider
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=               # Only if using OpenAI
ANTHROPIC_API_KEY=             # Only if using Anthropic
```

## AI Workflows

### IdeaStructuringService

**Input:** Raw idea (title + description)

**Output schema:**

```python
class StructuredIdea(BaseModel):
    title: str
    problem: str
    target_users: list[str]
    opportunity: str
    potential_solution: str
    assumptions: list[str]
    risks: list[str]
    unknowns: list[str]
```

**Flow:**

```
Raw idea text
    ↓
Build prompt (system prompt + user context)
    ↓
LLM provider.generate(prompt, response_model=StructuredIdea)
    ↓
Pydantic validation (reject if invalid)
    ↓
Persist structured_description on Idea
    ↓
Create AI_STRUCTURED activity event
    ↓
Return to user for review/edit
```

### ExecutionPlanningService

**Input:** Structured idea (with problem, opportunity, assumptions)

**Output schema:**

```python
class SuggestedAction(BaseModel):
    title: str
    description: str
    rationale: str
    estimated_effort: str | None = None

class ExecutionSuggestion(BaseModel):
    actions: list[SuggestedAction]  # max 5
    reasoning: str
```

**Key constraint:** Generate 3–5 focused next actions, not 50 generic tasks. Prioritize the smallest useful next action.

Each suggested action is marked `is_ai_generated = True` and requires explicit user acceptance.

## Error Handling

| Failure | Response |
|---------|----------|
| Provider unreachable | Return error to user, preserve their data, show retry option |
| Timeout | Same as unreachable |
| Invalid JSON from LLM | Log the raw output, retry once with a repair prompt, then fail gracefully |
| Schema validation failure | Log details, return partial result if possible, or ask user to retry |
| Rate limiting | Queue or backoff, inform user of delay |

**Invariant:** An AI failure never corrupts user data or persists invalid structured data.

## Evaluation

```
evals/
├── idea_structuring/
│   ├── test_cases.json       # Representative inputs
│   └── expectations.json     # Expected output characteristics
├── next_actions/
│   ├── test_cases.json
│   └── expectations.json
└── validation/
    ├── test_cases.json
    └── expectations.json
```

Evaluate against:
- **Schema validity** — Does output parse?
- **Completeness** — Are required fields populated meaningfully?
- **Hallucination** — Are claims grounded or fabricated?
- **Actionability** — Are suggested actions specific and doable?
- **Consistency** — Same input produces structurally similar output?
