.PHONY: help install test lint format docs docs-check dev-redis build up down logs clean export-openapi

PYTHON ?= ./venv/bin/python3
VENV ?= venv
PYTEST ?= $(VENV)/bin/pytest
RUFF ?= $(VENV)/bin/ruff
BANDIT ?= $(VENV)/bin/bandit

help: ## Show available developer commands
	@echo "=================================================================="
	@echo "🎓 Para Distributed Academic Operations Platform - Developer CLI"
	@echo "=================================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Initialize virtual environment and install production & dev dependencies
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt -r requirements-dev.txt

test: ## Execute complete test suite (546 tests)
	PYTHONPATH=. $(PYTEST) tests/ -v

test-fast: ## Execute test suite in quiet summary mode
	PYTHONPATH=. $(PYTEST) tests/ -q

lint: ## Execute strict Ruff linter and Bandit security AST analysis
	$(RUFF) check .
	$(BANDIT) -r services/ bot/ core/ api/ -c pyproject.toml

format: ## Automatically fix lint errors and format code
	$(RUFF) check . --fix
	$(RUFF) format .

docs: ## Regenerate 70 module engineering specifications and docs/index.md
	$(PYTHON) scripts/generate_docs_suite.py

docs-check: docs ## Verify that engineering documentation is in sync with codebase
	git diff --exit-code docs/

export-openapi: ## Export static OpenAPI JSON schema for REST API
	PYTHONPATH=. $(PYTHON) -c "import json; from api import create_app; open('docs/openapi.json', 'w').write(json.dumps(create_app().openapi(), indent=2))"

dev-redis: ## Spin up background Redis 7 persistence container
	docker run -d --name para-redis -p 6379:6379 redis:7-alpine redis-server --appendonly yes || docker start para-redis

build: ## Compile all microservice Docker containers in parallel
	docker compose build --parallel

up: ## Start all microservices in background (bot, api, worker, solver, redis)
	docker compose up -d

down: ## Stop all active microservices containers
	docker compose down

logs: ## Tail real-time aggregated logs from all services
	docker compose logs -f

clean: ## Remove temporary python caches and pytest artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache
