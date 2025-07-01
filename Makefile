.PHONY: test test-unit test-integration test-performance install-dev lint format clean help

# Default target
help:
	@echo "Available targets:"
	@echo "  install-dev      Install development dependencies"
	@echo "  test            Run all tests"
	@echo "  test-unit       Run unit tests only"
	@echo "  test-integration Run integration tests only (requires API key)"
	@echo "  test-performance Run performance tests only"
	@echo "  lint            Run linting checks"
	@echo "  format          Format code"
	@echo "  clean           Clean up temporary files"

# Install development dependencies
install-dev:
	pip install -e ".[test]"
	pip install black isort flake8

# Run all tests
test:
	pytest

# Run unit tests only (fast, no API calls)
test-unit:
	pytest -m "not integration and not performance"

# Run integration tests (requires API key)
test-integration:
	pytest -m "integration"

# Run performance tests
test-performance:
	pytest -m "performance"

# Run linting
lint:
	flake8 src tests
	isort --check-only src tests
	black --check src tests

# Format code
format:
	isort src tests
	black src tests

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf dist
	rm -rf build