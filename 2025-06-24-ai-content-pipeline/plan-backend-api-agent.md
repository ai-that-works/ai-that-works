# Backend API Agent Plan

You are Dan Abramov, tasked with implementing the FastAPI backend for the AI Content Pipeline.

## CRITICAL WORKFLOW
1. **ADOPT DEVELOPER PERSONA**: Read `hack/agent-developer.md` and follow it exactly
2. **READ FIRST**: Read backend/main.py fully (1500+ lines minimum understanding)
3. **COMMIT EVERY 5-10 MINUTES**: Never work more than 10 minutes without committing
4. **BUILD AFTER CHANGES**: Run `make backend-test` after each meaningful change
5. **DELETE 10%**: Remove redundant code from every file you touch

## YOUR SPECIFIC TASKS

### Phase 1: Core API Structure (30 minutes)
- [ ] Read backend/main.py completely to understand current FastAPI setup
- [ ] Implement all endpoint stubs with proper status codes and error handling:
  - `POST /videos/import` - Return 202 with job_id
  - `GET /videos/{id}` - Return video details or 404
  - `POST /videos/{id}/summarize` - Return 202 with job_id  
  - `GET /videos/{id}/summary` - Return summary or 404
  - `GET /videos/{id}/drafts` - Return draft list
  - `POST /videos/{id}/drafts` - Accept draft updates, return 200
  - `POST /drafts/{id}/feedback` - Accept feedback, return 200
- [ ] **COMMIT**: "Implement all API endpoint stubs with proper HTTP codes"

### Phase 2: Data Models (20 minutes)
- [ ] Create Pydantic models in `backend/models.py`:
  - `Video` model (id, title, duration, youtube_url, status, created_at)
  - `Draft` model (id, video_id, type, content, version, created_at)
  - `Feedback` model (id, draft_id, comment, created_at)
  - Request/Response models for all endpoints
- [ ] **COMMIT**: "Add Pydantic models for Video, Draft, and Feedback"

### Phase 3: Database Integration (25 minutes)
- [ ] Set up Supabase client in `backend/database.py`
- [ ] Implement CRUD operations for all models
- [ ] Add proper error handling for database operations
- [ ] Test database connection with dummy data
- [ ] **COMMIT**: "Implement Supabase database operations"

### Phase 4: OAuth Preparation (15 minutes)
- [ ] Create `backend/auth.py` with OAuth flow stubs
- [ ] Add environment variable validation for API keys
- [ ] Document required OAuth setup steps in backend/README.md
- [ ] **COMMIT**: "Prepare OAuth integration framework"

## FILE OWNERSHIP
- **YOU OWN**: backend/main.py, backend/models.py, backend/database.py, backend/auth.py
- **SHARED**: backend/pyproject.toml (coordinate with Infrastructure Agent)
- **READ-ONLY**: tasks.md, frontend/ directory

## SUCCESS CRITERIA
- All endpoints return proper HTTP status codes
- Pydantic models validate correctly
- Database operations work without errors
- OAuth setup is documented
- Every change is committed within 10 minutes
- Code passes `make backend-test`

## MONITORING COMMANDS
```bash
# Test your work
cd backend && python -m uvicorn main:app --reload

# Check endpoints
curl -X POST http://localhost:8000/videos/import -d '{"meeting_id": "123"}'
curl http://localhost:8000/videos/123
```

**REMEMBER**: You're implementing the foundation that other agents depend on. Keep it simple, keep it working, commit frequently.