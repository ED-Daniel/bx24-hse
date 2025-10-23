.PHONY: help format lint test clean

help:
	@echo "Available commands:"
	@echo "  make format  - Format code with black and isort"
	@echo "  make lint    - Run flake8 linter"
	@echo "  make test    - Run pytest"
	@echo "  make clean   - Remove cache files"
	@echo "  make all     - Format, lint and test"

format:
	@echo "Removing unused imports with autoflake..."
	autoflake --in-place --remove-all-unused-imports --remove-unused-variables app/ main.py -r
	@echo "Formatting code with black..."
	black app/ main.py
	@echo "Sorting imports with isort..."
	isort app/ main.py
	@echo "✅ Code formatted!"

lint:
	@echo "Running flake8..."
	flake8 app/ main.py
	@echo "✅ Linting complete!"

lint-fix:
	@echo "Auto-fixing with autoflake, black and isort..."
	autoflake --in-place --remove-all-unused-imports --remove-unused-variables app/ main.py -r
	black app/ main.py
	isort app/ main.py
	@echo "Running flake8..."
	-flake8 app/ main.py
	@echo "✅ Auto-fix complete!"

test:
	@echo "Running tests..."
	pytest tests/ -v
	@echo "✅ Tests complete!"

test-cov:
	@echo "Running tests with coverage..."
	pytest tests/ --cov=app --cov-report=html --cov-report=term
	@echo "✅ Coverage report generated!"

clean:
	@echo "Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cache cleaned!"

all: format lint test
	@echo "✅ All checks passed!"

docker-build:
	@echo "Building Docker image..."
	docker compose build
	@echo "✅ Docker image built!"

docker-up:
	@echo "Starting Docker containers..."
	docker compose up -d
	@echo "✅ Containers started!"

docker-down:
	@echo "Stopping Docker containers..."
	docker compose down
	@echo "✅ Containers stopped!"

docker-logs:
	@echo "Showing Docker logs..."
	docker compose logs -f app

docker-test:
	@echo "Running tests in Docker..."
	docker compose -f docker-compose.test.yml run --rm pytest
	@echo "✅ Docker tests complete!"
