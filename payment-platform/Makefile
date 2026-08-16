.PHONY: help install lint type-check test test-unit test-integration build up down logs clean load-test

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -e ".[dev]"

lint: ## Run linter (ruff)
	ruff check .
	ruff format --check .

format: ## Format code
	ruff format .
	ruff check --fix .

type-check: ## Run type checker (mypy)
	mypy services/ shared/ --ignore-missing-imports

test: ## Run all tests
	pytest tests/ -v --cov=services --cov=shared --cov-report=term-missing

test-unit: ## Run unit tests only
	pytest tests/unit/ -v

test-integration: ## Run integration tests
	pytest tests/integration/ -v

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## View logs
	docker-compose logs -f

clean: ## Remove all containers and volumes
	docker-compose down -v --remove-orphans

load-test: ## Run load tests with Locust
	cd load-tests && locust -f locustfile.py --headless -u 100 -r 10 -t 60s --host http://localhost:8000

security-scan: ## Run security scan
	bandit -r services/ shared/ -ll
