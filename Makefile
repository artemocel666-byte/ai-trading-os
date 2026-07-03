PYTHON ?= .venv/bin/python
UV ?= uv
COMPOSE ?= docker compose

.PHONY: install up down restart logs migrate migration test test-unit test-integration lint format typecheck check shell

install:
	$(UV) sync

up:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) down
	$(COMPOSE) up --build

logs:
	$(COMPOSE) logs --no-color -f

migrate:
	$(UV) run alembic upgrade head

migration:
	$(UV) run alembic revision --autogenerate -m "$(message)"

test:
	$(UV) run pytest

test-unit:
	$(UV) run pytest tests/unit

test-integration:
	$(UV) run pytest tests/integration

lint:
	$(UV) run ruff check .

format:
	$(UV) run ruff format .

typecheck:
	$(UV) run mypy app

check:
	$(UV) run ruff format --check .
	$(UV) run ruff check .
	$(UV) run mypy app
	$(UV) run pytest

shell:
	$(COMPOSE) exec api /bin/bash

