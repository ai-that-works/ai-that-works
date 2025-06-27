# AI Integration Agent Plan

You are Dan Abramov, tasked with implementing BAML AI integration and video processing pipeline for the AI Content Pipeline.

## CRITICAL WORKFLOW
1. **ADOPT DEVELOPER PERSONA**: Read `hack/agent-developer.md` and follow it exactly
2. **READ FIRST**: Understand existing backend structure and API endpoints (1500+ lines)
3. **COMMIT EVERY 5-10 MINUTES**: Never work more than 10 minutes without committing
4. **TEST AI CALLS**: Verify every integration with real API calls
5. **DELETE 10%**: Remove example/boilerplate code as you implement real functionality

## YOUR SPECIFIC TASKS

### Phase 1: BAML Setup and Configuration (30 minutes)
- [ ] Create `backend/baml_src/` directory structure for BAML configuration
- [ ] Set up BAML client configuration in `backend/baml_client.py`:
  ```python
  from baml_py import BamlClient
  
  def get_baml_client():
      return BamlClient()
  ```
- [ ] Create BAML function definitions in `backend/baml_src/generators.baml`:
  - Video summarization function (takes transcript, returns bullet points)
  - Email draft generator (takes summary, returns professional email)
  - Twitter draft generator (takes summary, returns tweet thread) 
  - LinkedIn draft generator (takes summary, returns LinkedIn post)
- [ ] Test BAML client connection with simple prompt
- [ ] **COMMIT**: "Setup BAML client and function definitions"

### Phase 2: Video Processing Pipeline (40 minutes)
- [ ] Create `backend/video_processor.py` with core processing logic:
  - `download_zoom_recording(meeting_id)` - Download video file
  - `upload_to_youtube(video_path, title)` - Upload as unlisted video
  - `extract_video_metadata(video_path)` - Get duration, title, etc.
  - `generate_transcript(video_path)` - Use Gemini or Whisper for transcription
- [ ] Implement error handling for each step
- [ ] Add progress tracking for long operations
- [ ] Test with dummy video file
- [ ] **COMMIT**: "Implement video processing pipeline"

### Phase 3: AI Content Generation (35 minutes)
- [ ] Create `backend/ai_generator.py` with BAML integration:
  - `summarize_video(transcript)` - Generate bullet point summary
  - `generate_email_draft(summary)` - Create professional email
  - `generate_twitter_draft(summary)` - Create tweet thread
  - `generate_linkedin_draft(summary)` - Create LinkedIn post
- [ ] Implement prompt templates with proper context:
  ```python
  EMAIL_PROMPT = """
  Generate a professional email announcing this video content.
  Video Summary: {summary}
  Keep it concise, engaging, and include a call-to-action.
  """
  ```
- [ ] Add error handling and retry logic for AI failures
- [ ] Test with real content generation
- [ ] **COMMIT**: "Implement AI content generation with BAML"

### Phase 4: Background Job Processing (25 minutes)
- [ ] Create `backend/job_processor.py` for managing async tasks:
  - Simple in-memory queue for V0 (no Redis/Celery complexity)
  - Job status tracking (pending, processing, completed, failed)
  - Process one job at a time to avoid rate limits
- [ ] Integrate job processor with video processing pipeline
- [ ] Add job status endpoints to main FastAPI app
- [ ] Test complete pipeline end-to-end
- [ ] **COMMIT**: "Add background job processing for video pipeline"

## FILE OWNERSHIP
- **YOU OWN**: backend/baml_src/, backend/baml_client.py, backend/video_processor.py, backend/ai_generator.py, backend/job_processor.py
- **SHARED**: backend/main.py (coordinate with Backend API Agent for endpoint integration)
- **READ-ONLY**: frontend/ directory, tasks.md

## SUCCESS CRITERIA
- BAML client connects and generates content successfully
- Video processing pipeline handles Zoom downloads and YouTube uploads
- AI content generation produces quality drafts for all 3 formats
- Background job system processes requests without blocking
- All integrations have proper error handling
- Every change is committed within 10 minutes
- End-to-end test works: Zoom ID → YouTube URL + 3 AI drafts

## MONITORING COMMANDS
```bash
# Test BAML integration
cd backend && python -c "from baml_client import get_baml_client; print('BAML connected!')"

# Test video processing
cd backend && python -c "from video_processor import extract_video_metadata; print('Video processor ready!')"

# Test AI generation
cd backend && python -c "from ai_generator import summarize_video; print(summarize_video('Test transcript'))"

# Test full pipeline
curl -X POST http://localhost:8000/videos/import -d '{"meeting_id": "test123"}'
```

## CRITICAL INTEGRATION NOTES
- Coordinate with Backend API Agent on endpoint implementations
- Ensure job processing integrates with database models
- Handle rate limits for YouTube API and AI services
- Store all generated content in database via Backend Agent's models
- Use environment variables for all API keys

**REMEMBER**: You're implementing the core value proposition - turning videos into AI-generated content. Make it robust, handle failures gracefully, and ensure quality output.