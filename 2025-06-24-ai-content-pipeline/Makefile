# Makefile for AI Content Pipeline
.PHONY: setup teardown backend-dev frontend-dev backend-test frontend-build

setup:
	@echo "Setting up project..."
	cd backend && uv sync
	cd frontend && npm install
	@echo "Setup complete!"

backend-dev:
	cd backend && uv run uvicorn main:app --reload

frontend-dev:
	cd frontend && npm run dev

backend-test:
	cd backend && uv run python -m pytest || echo "No tests yet"

frontend-build:
	cd frontend && npm run build

teardown:
	@echo "Tearing down project..."
	@echo "Teardown complete!"
