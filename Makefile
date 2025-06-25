.PHONY: help install install-dev test test-cov lint format clean docker-build docker-up docker-down docker-logs

help: ## Show this help message
	@echo "Universal Time Tracker - Development Commands"
	@echo "============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r server/requirements.txt

install-dev: ## Install development dependencies
	pip install -r server/requirements-dev.txt
	pre-commit install

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=server/src --cov-report=html --cov-report=term-missing

lint: ## Run linting checks
	flake8 server/src cli
	mypy server/src cli
	bandit -r server/src

format: ## Format code with black and isort
	black server/src cli
	isort server/src cli

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf build
	rm -rf dist

docker-build: ## Build Docker image
	docker-compose build

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## Show Docker logs
	docker-compose logs -f

docker-restart: ## Restart Docker containers
	docker-compose restart

setup: install-dev ## Setup development environment
	@echo "Development environment setup complete!"
	@echo "Run 'make docker-up' to start the application"

dev: ## Start development server
	python start_server.py

check: format lint test ## Run all checks (format, lint, test) 