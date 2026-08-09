.PHONY: help install test test-unit typecheck lint lint-fix format docker-up docker-down clean

# Default target
help:
	@echo "CodeGraph AI - Development Automation"
	@echo ""
	@echo "Usage:"
	@echo "  make install        Install project dependencies using uv"
	@echo "  make test           Run the full test suite"
	@echo "  make test-unit      Run unit tests (e.g., docker-compose verification)"
	@echo "  make typecheck      Run Mypy static type checking"
	@echo "  make lint           Run Ruff code linting checks"
	@echo "  make lint-fix       Run Ruff and auto-fix safe lint violations"
	@echo "  make format         Format code using Black and Ruff"
	@echo "  make docker-up      Start local services via Docker Compose"
	@echo "  make docker-down    Stop local Docker services"
	@echo "  make clean          Clean up build artifacts and cache files"

install:
	uv sync --all-extras

test:
	uv run pytest

test-unit:
	uv run pytest tests/unit/test_docker_compose.py

lint:
# Linting with auto-fix enabled
	uv run ruff check --fix .
# Code Formatting
	uv run ruff format .
# Typechecking
	uv run mypy .

docker-up:
	docker compose up -d

docker-down:
	docker compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +