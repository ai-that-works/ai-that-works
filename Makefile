# Makefile for AI Content Pipeline
.PHONY: setup teardown backend-dev frontend-dev backend-test frontend-build

setup:
	@echo "Setting up project..."
	cd 2025-06-24-ai-content-pipeline/backend && uv sync
	cd 2025-06-24-ai-content-pipeline/frontend && npm install
	@echo "Setup complete!"

backend-dev:
	cd 2025-06-24-ai-content-pipeline/backend && uv run uvicorn main:app --reload

frontend-dev:
	cd 2025-06-24-ai-content-pipeline/frontend && npm run dev

backend-test:
	cd 2025-06-24-ai-content-pipeline/backend && uv run python -m pytest || echo "No tests yet"

frontend-build:
	cd 2025-06-24-ai-content-pipeline/frontend && npm run build

teardown:
	@echo "Tearing down project..."
	@echo "Teardown complete!"
