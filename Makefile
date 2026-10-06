.PHONY: help install dev test lint format check migrate clean

help:
	@echo "Available commands:"
	@echo "  make dev      - Run local development server"
	@echo "  make test     - Run pytest test suite"
	@echo "  make lint     - Run ruff check and mypy"
	@echo "  make format   - Run ruff format and ruff check --fix"
	@echo "  make check    - Run lint and test"
	@echo "  make migrate  - Run alembic migrations"

install:
	uv sync --extra dev

dev:
	uv run uvicorn idea_tracker.main:app --reload --host 127.0.0.1 --port 8000

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run mypy src

format:
	uv run ruff format .
	uv run ruff check --fix .

check: lint test

migrate:
	uv run alembic upgrade head

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
