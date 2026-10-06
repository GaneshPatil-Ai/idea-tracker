"""Tests for configuration management."""

from idea_tracker.config.settings import AppEnv, LLMProviderType, Settings


def test_default_settings() -> None:
    """Verify default settings values."""
    s = Settings()
    assert s.app_name == "Idea Tracker"
    assert s.app_env == AppEnv.DEVELOPMENT
    assert s.llm_provider == LLMProviderType.OLLAMA
    assert s.host == "127.0.0.1"
    assert s.port == 8000


def test_is_testing_property() -> None:
    """Verify is_testing helper property."""
    s = Settings(app_env=AppEnv.TESTING)
    assert s.is_testing is True

    s_dev = Settings(app_env=AppEnv.DEVELOPMENT)
    assert s_dev.is_testing is False
