# Infrastructure Agent Plan

You are Dan Abramov, tasked with setting up the database, OAuth, and deployment infrastructure for the AI Content Pipeline.

## CRITICAL WORKFLOW
1. **ADOPT DEVELOPER PERSONA**: Read `hack/agent-developer.md` and follow it exactly
2. **READ FIRST**: Read backend/env.template and frontend/env.template fully
3. **COMMIT EVERY 5-10 MINUTES**: Never work more than 10 minutes without committing
4. **TEST CONNECTIONS**: Verify every integration with simple test calls
5. **DELETE 10%**: Remove example/template code as you implement real functionality

## YOUR SPECIFIC TASKS

### Phase 1: Supabase Database Setup (30 minutes)
- [ ] Create new Supabase project (document project URL and keys)
- [ ] Design database schema with proper relationships:
  ```sql
  -- Videos table
  CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    duration INTEGER,
    youtube_url TEXT,
    status TEXT NOT NULL DEFAULT 'importing',
    zoom_meeting_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
  );
  
  -- Drafts table  
  CREATE TABLE drafts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id UUID REFERENCES videos(id),
    type TEXT NOT NULL, -- 'email', 'twitter', 'linkedin'
    content TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
  );
  
  -- Feedback table
  CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    draft_id UUID REFERENCES drafts(id),
    comment TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
  );
  ```
- [ ] Set up Row Level Security (RLS) policies for multi-user support
- [ ] **COMMIT**: "Create Supabase database schema with RLS policies"

### Phase 2: OAuth Configuration (40 minutes)
- [ ] Create Google Cloud Console project for YouTube API
- [ ] Generate OAuth 2.0 credentials for YouTube uploads
- [ ] Document the OAuth setup process in `docs/oauth-setup.md`:
  - Step-by-step Google Cloud Console setup
  - Required scopes and permissions
  - Local development token generation
- [ ] Set up Zoom API credentials (document required environment variables)
- [ ] Create `backend/oauth_setup.py` script to help with token generation
- [ ] **COMMIT**: "Setup OAuth credentials and documentation"

### Phase 3: Environment Configuration (20 minutes)
- [ ] Update backend/env.template with all required variables:
  ```
  SUPABASE_URL=
  SUPABASE_ANON_KEY=
  SUPABASE_SERVICE_KEY=
  GOOGLE_CLIENT_ID=
  GOOGLE_CLIENT_SECRET=
  ZOOM_API_KEY=
  ZOOM_API_SECRET=
  BAML_API_KEY=
  ```
- [ ] Update frontend/env.template:
  ```
  NEXT_PUBLIC_SUPABASE_URL=
  NEXT_PUBLIC_SUPABASE_ANON_KEY=
  ```
- [ ] Create example .env files (with placeholder values)
- [ ] **COMMIT**: "Update environment templates with all required secrets"

### Phase 4: Development Tooling (30 minutes)
- [ ] Create comprehensive Makefile with all development commands:
  ```makefile
  backend-dev:
  	cd backend && uvicorn main:app --reload
  
  frontend-dev:
  	cd frontend && npm run dev
  
  backend-test:
  	cd backend && python -m pytest
  
  frontend-build:
  	cd frontend && npm run build
  
  setup:
  	cd backend && uv sync
  	cd frontend && npm install
  ```
- [ ] Add database migration scripts if needed
- [ ] Create docker-compose.yml for local development (optional)
- [ ] **COMMIT**: "Add comprehensive development tooling and Makefile"

## FILE OWNERSHIP
- **YOU OWN**: Makefile, backend/env.template, frontend/env.template, docs/oauth-setup.md
- **SHARED**: backend/pyproject.toml, frontend/package.json (coordinate with other agents)  
- **CREATE**: backend/oauth_setup.py, database migration scripts

## SUCCESS CRITERIA
- Supabase database is created with proper schema
- OAuth credentials are documented and testable
- Environment templates include all required variables
- Makefile provides easy development commands
- Every setup step is documented
- Every change is committed within 10 minutes

## MONITORING COMMANDS
```bash
# Test Supabase connection
curl -X GET "https://your-project.supabase.co/rest/v1/videos" \
  -H "apikey: your-anon-key"

# Test backend with environment
cd backend && python -c "from database import supabase_client; print('Connected!')"

# Test OAuth setup
cd backend && python oauth_setup.py
```

## CRITICAL INTEGRATION NOTES
- Document ALL secret keys and setup processes clearly
- Test each integration before moving to next phase
- Coordinate with Backend Agent on database models
- Ensure environment variables match across backend/frontend

**REMEMBER**: Other agents depend on your infrastructure working correctly. Test everything, document everything, make setup foolproof.