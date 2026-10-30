.PHONY: help install test lint type-check format docs docs-check dev-redis build up down logs clean export-openapi

PYTHON ?= $(shell if [ -f ./venv/bin/python3 ]; then echo "./venv/bin/python3"; else echo "python3"; fi)
VENV ?= venv
PYTEST ?= $(VENV)/bin/pytest
RUFF ?= $(VENV)/bin/ruff
BANDIT ?= $(VENV)/bin/bandit
MYPY ?= $(VENV)/bin/mypy

help: ## Show available developer commands
	@echo "=================================================================="
	@echo "🎓 Para Distributed Academic Operations Platform - Developer CLI"
	@echo "=================================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Initialize virtual environment and install production & dev dependencies
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt -r requirements-dev.txt

test: ## Execute complete test suite (754 tests)
	PYTHONPATH=. $(PYTEST) tests/ -v

test-fast: ## Execute test suite in quiet summary mode
	PYTHONPATH=. $(PYTEST) tests/ -q

test-cov: ## Execute test suite with terminal and XML coverage report
	PYTHONPATH=. $(PYTEST) tests/ --cov=. --cov-report=term:skip-covered --cov-report=xml:coverage.xml -q

load-test: ## Execute 500+ RPS load benchmark suite via Locust
	./scripts/run_load_test.sh

compile-deps: ## Compile deterministic requirements.lock from requirements.txt via pip-compile
	$(VENV)/bin/pip-compile --output-file=requirements.lock --strip-extras requirements.txt

lint: ## Execute strict Ruff linter and Bandit security AST analysis
	$(RUFF) check .
	$(BANDIT) -r services/ bot/ core/ api/ -c pyproject.toml

type-check: ## Execute static type analysis with MyPy
	$(MYPY)

format: ## Automatically fix lint errors and format code
	$(RUFF) check . --fix
	$(RUFF) format .

docs: ## Regenerate 100 module engineering specifications and docs/index.md
	$(PYTHON) scripts/generate_docs_suite.py

docs-check: docs ## Verify that engineering documentation is in sync with codebase
	git diff --exit-code docs/

export-openapi: ## Export static OpenAPI JSON schema for REST API
	PYTHONPATH=. $(PYTHON) -c "import json; from api import create_app; open('docs/openapi.json', 'w').write(json.dumps(create_app().openapi(), indent=2) + '\n')"

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
