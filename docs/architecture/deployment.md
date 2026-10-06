# Deployment

## Local Development

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (package manager)

### Setup

```bash
# Clone the repository
git clone https://github.com/your-org/idea-tracker.git
cd idea-tracker

# Copy environment configuration
cp .env.example .env
# Edit .env with your settings (optional — defaults work for local dev)

# Install dependencies and sync environment
uv sync

# Run database migrations
uv run alembic upgrade head

# Start the development server
uv run uvicorn src.idea_tracker.main:app --reload --host 0.0.0.0 --port 8000
```

Open [http://localhost:8000](http://localhost:8000).

### Running Tests

```bash
uv run pytest
uv run ruff check .
uv run mypy src/
```

## Docker

### Dockerfile

The application ships with a multi-stage Dockerfile:

1. **Build stage** — installs dependencies with uv
2. **Runtime stage** — minimal image with only runtime dependencies

```bash
# Build
docker build -t idea-tracker .

# Run
docker run -p 8000:8000 -v idea-tracker-data:/app/data idea-tracker
```

The SQLite database is stored in `/app/data/` inside the container. Mount a volume to persist data across container restarts.

### Docker Compose

For the simplest possible setup:

```bash
docker compose up
```

The `docker-compose.yml` provides:
- The application on port 8000
- Persistent volume for SQLite data
- Optional Ollama service for local AI

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - idea-data:/app/data
    env_file:
      - .env

  # Optional: local AI via Ollama
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    profiles:
      - ai

volumes:
  idea-data:
  ollama-data:
```

To include Ollama: `docker compose --profile ai up`

## Environment Configuration

All configuration is via environment variables. See `.env.example` for the full list.

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | Environment: `development`, `production` |
| `DATABASE_URL` | `sqlite:///data/ideas.db` | SQLite database path |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LLM_PROVIDER` | `none` | AI provider: `none`, `ollama`, `openai`, `anthropic` |
| `LLM_MODEL` | — | Model name for the configured provider |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `OPENAI_API_KEY` | — | OpenAI API key (only if provider is `openai`) |
| `ANTHROPIC_API_KEY` | — | Anthropic API key (only if provider is `anthropic`) |

### Security Notes

- **Never commit `.env`** — it is in `.gitignore`
- `.env.example` contains placeholder values only
- API keys are only required when using the corresponding AI provider
- The application is fully functional without any AI provider configured
