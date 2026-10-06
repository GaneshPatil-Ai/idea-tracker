from pydantic import BaseModel

class Settings(BaseModel):
    # AI Configuration
    LLM_PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "llama3.2"
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Database
    DATABASE_URL: str = "sqlite:///ideas.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
