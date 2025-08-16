---
date: 2025-08-16T11:07:26-07:00
researcher: dex
git_commit: 0a670a4d771a4a57ee2e51dcd99aedab236f3d1f
branch: main
repository: ai-that-works
topic: "Zoom and Luma API CLI Script Research for 2025-07-01-ai-content-pipeline-2"
tags: [research, codebase, zoom, luma, cli, api-integration, content-pipeline]
status: complete
last_updated: 2025-08-16
last_updated_by: dex
---

# Research: Zoom and Luma API CLI Script Research for 2025-07-01-ai-content-pipeline-2

**Date**: 2025-08-16T11:07:26-07:00
**Researcher**: dex
**Git Commit**: 0a670a4d771a4a57ee2e51dcd99aedab236f3d1f
**Branch**: main
**Repository**: ai-that-works

## Research Question
Convert the fetching of Zoom meetings and Luma events from the API into small CLI scripts that can be run locally and piped together. Research existing implementations in 2025-07-01-ai-content-pipeline-2 to identify exact file names, line numbers, and code samples needed to create TypeScript scripts in BUN for a new tools folder.

## Summary
The codebase contains complete working implementations of both Zoom and Luma API integrations in the 2025-07-01-ai-content-pipeline-2 project. The Zoom client uses OAuth 2.0 Server-to-Server authentication with automatic token refresh, while the Luma client uses API key authentication. Both implementations include comprehensive error handling, data models, and integration patterns suitable for adaptation into standalone CLI scripts.

## Detailed Findings

### Zoom Meeting Fetching Implementation

**Core Client**: `2025-07-01-ai-content-pipeline-2/backend/zoom_client.py`
- **Authentication** (lines 33-58): OAuth 2.0 Server-to-Server flow with automatic token refresh
- **Token Management** (lines 60-93): Caches tokens in `zoom_token.json`, validates expiry
- **Get Recordings** (lines 95-147): Paginated fetching with date filtering
  ```python
  def get_recordings(self, from_date=None, to_date=None, page_size=100):
      # Default to last 30 days if no dates provided
      # Returns grouped meetings with all recording types
  ```
- **Get Transcript** (lines 149-183): Downloads VTT transcripts with proper headers
- **Recording Details** (lines 185-210): Fetches detailed recording metadata

**API Endpoints** (`backend/main.py`):
- `GET /zoom/recordings` (lines 1046-1077): Returns grouped meetings
- `GET /test/zoom` (lines 1018-1043): Tests API credentials
- `GET /zoom/recordings/{meeting_id}/luma-match` (lines 1079-1093): Matches with Luma events

**Environment Variables** (`backend/env.template`):
```bash
ZOOM_ACCOUNT_ID=your_zoom_account_id_here
ZOOM_CLIENT_ID=your_zoom_client_id_here  
ZOOM_CLIENT_SECRET=your_zoom_client_secret_here
```

**Data Models** (`backend/models.py`):
- `ZoomRecording` (lines 89-101): Individual recording metadata
- `ZoomMeetingRecordings` (lines 146-156): Grouped recordings by meeting

### Luma Event Fetching Implementation

**Core Client**: `2025-07-01-ai-content-pipeline-2/backend/luma_client.py`
- **Authentication** (lines 16-23): API key-based with headers setup
- **Get Recent Events** (lines 58-95): Fetches past events from calendar
  ```python
  def _get_recent_past_events(self, limit=10):
      url = f"{self.base_url}/calendar/list-events"
      params = {"calendar_api_id": self.calendar_id, "period": "past"}
  ```
- **Event Matching** (lines 25-56): Matches Zoom meetings to Luma events by date/ID
- **Next Event Finding** (lines 122-145): Uses BAML AI to identify next "AI that works" event

**API Configuration**:
- Base URL: `https://public-api.lu.ma/public/v1`
- Authentication: `x-luma-api-key` header
- Environment: `LUMA_API_KEY`

**Data Models** (`backend/models.py`):
- `LumaEvent` (lines 160-168): Event metadata with optional fields

**Response Structure** (lines 96-121):
```json
{
  "api_id": "evt-7AfHSGOBmoz4iLO",
  "event": {
    "name": "🦄 ai that works: Memory from scratch",
    "start_at": "2025-07-08T17:00:00.000Z",
    "url": "https://lu.ma/7sfm30gu",
    "zoom_meeting_url": "https://us06web.zoom.us/j/84317818466?pwd=..."
  }
}
```

### TypeScript/CLI Patterns

**Frontend API Client** (`frontend/src/lib/apiClient.ts`):
- Environment-based configuration (lines 7, 19-29)
- Centralized error handling (lines 31-40)
- Typed API methods (lines 50-182)

**CLI Script Pattern** (`2025-06-03-humans-as-tools-async/src/cli.ts`):
- Command-line args (lines 42-49)
- Module execution check (lines 172-174)
- Interactive prompts (lines 137-148)

**Key Dependencies**:
- No Bun-specific code found; projects use Node.js with tsx
- Native fetch preferred over axios
- `fs.writeFileSync` for file operations
- Environment variables for configuration

## Code References

### Zoom Implementation
- `2025-07-01-ai-content-pipeline-2/backend/zoom_client.py:33-58` - OAuth authentication
- `2025-07-01-ai-content-pipeline-2/backend/zoom_client.py:95-147` - Recording fetching
- `2025-07-01-ai-content-pipeline-2/backend/zoom_client.py:149-183` - Transcript download
- `2025-07-01-ai-content-pipeline-2/backend/models.py:89-101` - ZoomRecording model
- `2025-07-01-ai-content-pipeline-2/backend/main.py:1046-1077` - API endpoint

### Luma Implementation  
- `2025-07-01-ai-content-pipeline-2/backend/luma_client.py:16-23` - API key setup
- `2025-07-01-ai-content-pipeline-2/backend/luma_client.py:58-95` - Event fetching
- `2025-07-01-ai-content-pipeline-2/backend/luma_client.py:25-56` - Event matching
- `2025-07-01-ai-content-pipeline-2/backend/models.py:160-168` - LumaEvent model
- `2025-07-01-ai-content-pipeline-2/backend/baml_src/content_generation.baml:512-544` - AI event identification

### TypeScript Patterns
- `2025-07-01-ai-content-pipeline-2/frontend/src/lib/apiClient.ts:7-40` - API client setup
- `2025-06-03-humans-as-tools-async/src/cli.ts:42-49` - CLI argument handling
- `2025-06-03-humans-as-tools-async/src/cli.ts:172-174` - Module execution pattern

## Architecture Insights

1. **Authentication Patterns**:
   - Zoom uses OAuth 2.0 with token caching and refresh
   - Luma uses simple API key authentication
   - Both store credentials in environment variables

2. **Data Fetching Strategies**:
   - Zoom: Paginated requests with date filtering
   - Luma: Single request for event lists
   - Both handle errors gracefully with fallbacks

3. **Matching Logic**:
   - Extract Zoom meeting IDs from URLs using regex
   - Match by date and meeting ID correlation
   - AI-powered event identification for specific content

4. **File Output Patterns**:
   - Python uses JSON for data persistence
   - TypeScript uses fs.writeFileSync for file operations
   - Markdown generation follows template patterns

## Historical Context (from thoughts/)

- `2025-07-01-ai-content-pipeline-2/architecture.md` - Complete OAuth-based Zoom system with real-time processing
- `2025-07-01-ai-content-pipeline-2/specs/github-pr-integration-plan.md` - Manual PR triggers and template-based generation
- `.claude/commands/episode_prep.md` - Step-by-step validation and progress tracking patterns

## Related Research
- Previous content pipeline implementations in the 2025-07-01 project
- GitHub PR integration patterns for automated content generation

## Open Questions
1. Should the CLI scripts use Bun's native APIs or maintain Node.js compatibility?
2. What format should the markdown output follow - existing episode template or custom?
3. Should scripts support piping/streaming or batch processing?
4. How should authentication credentials be managed for CLI usage?