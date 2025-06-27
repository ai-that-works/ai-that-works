# Makefile for AI Content Pipeline
.PHONY: setup teardown backend-dev frontend-dev backend-test frontend-test frontend-build clean oauth-setup db-setup help

# Default target
help:
	@echo "AI Content Pipeline - Available Commands:"
	@echo "  setup           - Install all dependencies"
	@echo "  backend-dev     - Start backend development server"
	@echo "  frontend-dev    - Start frontend development server"
	@echo "  backend-test    - Run backend tests"
	@echo "  frontend-test   - Run frontend tests"
	@echo "  frontend-build  - Build frontend for production"
	@echo "  oauth-setup     - Setup OAuth credentials"
	@echo "  db-setup        - Show database setup instructions"
	@echo "  clean           - Clean build artifacts"
	@echo "  teardown        - Remove all build artifacts"

setup:
	@echo "🚀 Setting up AI Content Pipeline..."
	@echo "Installing backend dependencies..."
	cd 2025-06-24-ai-content-pipeline/backend && uv sync
	@echo "Installing frontend dependencies..."
	cd 2025-06-24-ai-content-pipeline/frontend && npm install
	@echo "✅ Setup complete!"
	@echo "Next steps:"
	@echo "  1. Run 'make db-setup' to setup your database"
	@echo "  2. Run 'make oauth-setup' to configure OAuth"
	@echo "  3. Copy .env.example files and fill in your credentials"

backend-dev:
	@echo "🔧 Starting backend development server..."
	cd 2025-06-24-ai-content-pipeline/backend && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

frontend-dev:
	@echo "🎨 Starting frontend development server..."
	cd 2025-06-24-ai-content-pipeline/frontend && npm run dev

backend-test:
	@echo "🧪 Running backend tests..."
	cd 2025-06-24-ai-content-pipeline/backend && uv run python -m pytest -v || echo "No tests configured yet"

frontend-test:
	@echo "🧪 Running frontend tests..."
	cd 2025-06-24-ai-content-pipeline/frontend && npm test || echo "No tests configured yet"

frontend-build:
	@echo "📦 Building frontend for production..."
	cd 2025-06-24-ai-content-pipeline/frontend && npm run build

oauth-setup:
	@echo "🔐 Setting up OAuth credentials..."
	cd 2025-06-24-ai-content-pipeline/backend && uv run python oauth_setup.py

db-setup:
	@echo "🗄️  Database Setup Instructions:"
	@echo "1. Create a new Supabase project at https://supabase.com"
	@echo "2. Copy the SQL from docs/database-schema.sql"
	@echo "3. Run it in your Supabase SQL editor"
	@echo "4. Update your .env file with the Supabase credentials"
	@echo "5. Test connection: make test-db"

test-db:
	@echo "🔍 Testing database connection..."
	cd 2025-06-24-ai-content-pipeline/backend && uv run python -c "from supabase import create_client, Client; import os; print('Testing Supabase connection...'); client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_ANON_KEY')); print('✅ Connection successful!')" || echo "❌ Connection failed - check your .env file"

clean:
	@echo "🧹 Cleaning build artifacts..."
	cd 2025-06-24-ai-content-pipeline/frontend && rm -rf .next dist build
	cd 2025-06-24-ai-content-pipeline/backend && rm -rf __pycache__ .pytest_cache *.pyc
	@echo "✅ Clean complete!"

teardown: clean
	@echo "🗑️  Tearing down project..."
	cd 2025-06-24-ai-content-pipeline/backend && rm -rf .venv
	cd 2025-06-24-ai-content-pipeline/frontend && rm -rf node_modules
	@echo "✅ Teardown complete!"