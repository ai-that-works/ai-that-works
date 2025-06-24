# V0 MVP Tasks - AI Content Pipeline

## 🎯 V0 SCOPE: Zoom → YouTube → AI Drafts → Web UI
**Focus**: Turn Zoom recordings into unlisted YouTube videos + 3 AI-generated text drafts (email, X, LinkedIn) with human review/editing UI.

---

## 📋 BACKEND TASKS (Python + FastAPI)

### 1. Core Dependencies & Setup
- [x] Add missing dependencies to `pyproject.toml`:
  - [x] `uvicorn[standard]` (ASGI server)
  - [x] `python-multipart` (file uploads)
  - [x] `httpx` (HTTP client for APIs)
  - [x] `python-dotenv` (environment variables)
  - [x] `supabase` (database client)
  - [x] `google-auth` + `google-auth-oauthlib` (YouTube API)
  - [x] `google-api-python-client` (YouTube upload)
  - [x] `baml-py` (AI client)
- [x] Create `.env` template with required secrets
- [x] Set up basic FastAPI app structure with CORS
- [x] implement all endpoints with no logic, just return dummy data, to get the contract baked so frontend devs can start working, we'll fill in the endpoints as we go
  - [x] `POST /videos/import` - Queue Zoom download
  - [x] `GET /videos/{id}` - Get video details + drafts
  - [x] `POST /videos/{id}/summarize` - Trigger Gemini pipeline
  - [x] `GET /videos/{id}/summary` - Get summary points
  - [x] `GET /videos/{id}/drafts` - List draft history
  - [x] `POST /videos/{id}/drafts` - Save edited drafts
  - [x] `POST /drafts/{id}/feedback` - Add feedback

### 2. Database Schema & Supabase Setup
- [ ] Create Supabase project
- [ ] Implement database schema (videos, drafts, feedback tables)
- [ ] Set up Supabase client configuration
- [ ] Add RLS policies for user isolation

### 3. OAuth Integration (for localhost ONLY)
- [ ] Implement Zoom OAuth flow - we'll use a server token from ZOOM_API_KEY and other needed things - consult me when you're ready for these things - output instructions for how to get the key
- [ ] Implement Google/YouTube OAuth flow - just use a google_credentials file that I'll provide, and walk me through the local oauth flow to get the tokens.json file locally, and just store it (use refresh token in the token json before making calls)

### 4. Core API Endpoints
implement each endpoint one at a time, test with curl

- [ ] `POST /videos/import` - Queue Zoom download
- [ ] `GET /videos/{id}` - Get video details + drafts
- [ ] `POST /videos/{id}/summarize` - Trigger Gemini pipeline
- [ ] `GET /videos/{id}/summary` - Get summary points
- [ ] `GET /videos/{id}/drafts` - List draft history
- [ ] `POST /videos/{id}/drafts` - Save edited drafts
- [ ] `POST /drafts/{id}/feedback` - Add feedback

### 5. Video Processing Pipeline
- [ ] Download Zoom recording to backend
- [ ] Upload video to YouTube as unlisted
- [ ] Extract video metadata (title, duration, etc.)
- [ ] Store video info in database

### 6. AI Integration (BAML)
- [ ] Set up BAML client configuration
- [ ] Create prompt templates for:
  - Video summarization (bullet points)
  - Email draft generation
  - X/Twitter draft generation
  - LinkedIn draft generation
- [ ] Implement Gemini 2.5 Pro integration
- [ ] Add error handling for AI failures

### 7. Background Processing
- [ ] Implement simple job queue (in-memory or basic file-based)
- [ ] Process one recording at a time
- [ ] Handle job failures gracefully

---

## 🎨 FRONTEND TASKS (Next.js + TypeScript)

### 1. Dependencies & Setup
- [ ] Add missing dependencies:
  - `@supabase/supabase-js` (database client)
  - `@radix-ui/react-*` (shadcn components)
  - `class-variance-authority` (component variants)
  - `clsx` + `tailwind-merge` (styling utilities)
  - `lucide-react` (icons)
  - `@hookform/resolvers` + `react-hook-form` (forms)
  - `zod` (validation)
- [ ] Set up shadcn/ui components
- [ ] Configure biome for linting
- [ ] Set up environment variables

### 2. Database Integration
- [ ] Configure Supabase client
- [ ] Set up real-time subscriptions
- [ ] Add authentication (basic email/password)

### 3. Core Pages & Components
- [ ] Dashboard page (`/`) - Video list with status badges
- [ ] Video detail page (`/videos/[id]`) - Player + draft editor
- [ ] Navigation component
- [ ] Video status badges component
- [ ] Draft editor component (textarea with save)
- [ ] Feedback component

### 4. Video Management UI
- [ ] Import video form (Zoom meeting ID input)
- [ ] Video list table with:
  - Status indicators
  - Title/duration
  - Created date
  - Action buttons
- [ ] Video detail view with:
  - Embedded YouTube player
  - Summary points display
  - Draft editing interface

### 5. Draft Editing Interface
- [ ] Three textarea fields (Email, X, LinkedIn)
- [ ] Pre-fill with AI-generated content
- [ ] Inline editing with save functionality
- [ ] Version history display
- [ ] Feedback input form

### 6. Real-time Updates
- [ ] Subscribe to video status changes
- [ ] Auto-refresh when drafts are updated
- [ ] Loading states for all async operations

---

## 🔧 INTEGRATION TASKS

### 1. API Integration
- [ ] Create TypeScript types for all API responses
- [ ] Implement API client functions
- [ ] Add error handling for API calls
- [ ] Add loading states for all operations

### 2. Environment Setup
- [ ] Create `.env.local` for frontend secrets
- [ ] Create `.env` for backend secrets
- [ ] Document all required environment variables

### 3. Development Workflow
- [ ] Set up hot reload for both frontend/backend
- [ ] Add basic error logging
- [ ] Test OAuth flows end-to-end
- [ ] Test video upload pipeline

---

## 🚫 OUT OF SCOPE (V0)
- CI/CD pipelines
- Advanced analytics
- Rich WYSIWYG editors
- Auto-publishing to social media
- Scheduling functionality
- Advanced job queues
- Complex retry logic
- Performance optimizations
- Advanced security features

---

## 🎯 SUCCESS CRITERIA
1. User can import Zoom recording via meeting ID
2. Video appears on YouTube as unlisted
3. AI generates 3 draft texts (email, X, LinkedIn)
4. User can edit drafts in web UI
5. All changes persist to database
6. Real-time updates work
7. Basic error handling in place

---

## 📝 NOTES
- Keep it simple - this is a hackathon project
- Focus on core functionality over polish
- Use existing libraries and tools
- Test manually rather than automated tests
- Deploy to local development only 