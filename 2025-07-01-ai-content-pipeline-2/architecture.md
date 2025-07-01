# AI Content Pipeline Architecture

## Overview

The AI Content Pipeline is an automated system that transforms Zoom recordings into multi-platform content using various AI services. It processes video recordings through transcription, summarization, and content generation stages, ultimately creating drafts for email newsletters, social media posts, and GitHub pull requests.

## Components

### Backend Services
- **FastAPI Server** (`backend/main.py`): Main API server handling all HTTP endpoints
- **Database Service** (`backend/database.py`): Supabase client for PostgreSQL operations
- **Zoom Client** (`backend/zoom_client.py`): OAuth-based Zoom API integration for fetching recordings
- **Video Processor** (`backend/video_processor.py`): Downloads Zoom recordings and uploads to YouTube
- **Luma Client** (`backend/luma_client.py`): Integration with Luma calendar for event matching
- **GitHub PR Service** (`backend/github_pr_service.py`): Creates PRs using Supersonic library
- **BAML Client** (`backend/baml_client/`): AI orchestration for content generation

### Frontend Components
- **Next.js App** (`frontend/src/app/`): React-based UI with real-time updates
- **Video List** (`frontend/src/components/home/video-list.tsx`): Displays processed videos
- **Zoom Recordings List** (`frontend/src/components/zoom/zoom-recordings-list.tsx`): Shows available Zoom meetings
- **Video Detail Page** (`frontend/src/app/videos/[id]/page.tsx`): Full video processing interface
- **Draft Editor** (`frontend/src/components/video/draft-editor.tsx`): Edit and refine AI-generated content
- **GitHub PR Button** (`frontend/src/components/github/CreateGitHubPRButton.tsx`): Manual PR creation trigger

### AI Functions (BAML)
- **SummarizeVideo**: Generates structured summary with bullet points, key topics, and takeaways
- **GenerateEmailDraft**: Creates newsletter draft in two stages (structure → full email)
- **GenerateTwitterThread**: Produces multi-tweet thread with hashtags
- **GenerateLinkedInPost**: Creates professional LinkedIn post
- **RefineEmailDraft/TwitterThread/LinkedInPost**: Iterates on content based on user feedback
- **GenerateYouTubeTitle**: Creates engaging video titles
- **DetermineEpisodePath**: Intelligently matches or creates episode folder names
- **GenerateEpisodeReadme**: Creates formatted episode documentation
- **GenerateRootReadmeUpdate**: Updates repository README with new episode

## Architecture Diagrams

### Loading Phase - Fetching Zoom Recordings and Matching to Luma Events

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant ZoomClient
    participant LumaClient
    participant Database

    User->>Frontend: Navigate to home page
    Frontend->>API: GET /zoom/recordings
    API->>ZoomClient: get_recordings(last_3_months)
    ZoomClient->>ZoomClient: OAuth token refresh if needed
    ZoomClient->>Zoom API: GET /users/me/recordings
    Zoom API-->>ZoomClient: Recording data
    ZoomClient-->>API: Formatted recordings list

    par For each recording
        API->>API: Group by meeting_id
        API->>LumaClient: get_event_for_zoom_meeting(meeting_id)
        LumaClient->>Luma API: Search events by date
        Luma API-->>LumaClient: Event matches
        LumaClient-->>API: Matched Luma event (if found)
    end

    API-->>Frontend: ZoomMeetingsResponse with Luma matches
    Frontend->>Frontend: Display recordings with import buttons
```

### Processing Phase - Complete Video Pipeline

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant BackgroundTasks
    participant VideoProcessor
    participant YouTube
    participant Database
    participant Supabase

    User->>Frontend: Click "Import & Process"
    Frontend->>API: POST /videos/import
    API->>Database: Create video record (status: processing)
    API->>BackgroundTasks: Queue complete_video_processing_pipeline
    API-->>Frontend: 202 Accepted (video_id)

    Note over BackgroundTasks: Async Processing Begins

    BackgroundTasks->>VideoProcessor: process_video(video_id, zoom_id)

    rect rgb(240, 240, 250)
        Note over VideoProcessor: Download Phase
        VideoProcessor->>Database: Update stage: "downloading"
        VideoProcessor->>VideoProcessor: Check cache for existing file
        alt Not cached
            VideoProcessor->>ZoomClient: Download recording
            ZoomClient->>Zoom API: GET recording file
            Zoom API-->>VideoProcessor: Video file stream
            VideoProcessor->>VideoProcessor: Save to cache
        end

        VideoProcessor->>ZoomClient: Get transcript (VTT format)
        ZoomClient-->>VideoProcessor: Transcript text
    end

    rect rgb(250, 240, 240)
        Note over VideoProcessor: Upload Phase
        VideoProcessor->>Database: Update stage: "uploading"
        VideoProcessor->>YouTube: Upload video
        YouTube-->>VideoProcessor: YouTube URL
        VideoProcessor->>Database: Update with YouTube URL & transcript
    end

    BackgroundTasks->>BackgroundTasks: Auto-trigger summarization
    BackgroundTasks->>API: process_video_summary(video_id)

    rect rgb(240, 250, 240)
        Note over API: Summarization Phase
        API->>Database: Update stage: "summarizing"
        API->>BAML: stream.SummarizeVideo(transcript)

        loop Streaming updates
            BAML-->>API: Partial summary
            API->>Database: Update summary in real-time
            Database->>Supabase: Trigger real-time event
            Supabase-->>Frontend: WebSocket update
            Frontend->>Frontend: Update UI immediately
        end

        BAML-->>API: Final summary
        API->>Database: Save complete summary
        API->>Database: Delete old drafts
    end

    rect rgb(250, 250, 240)
        Note over API: Content Generation Phase
        API->>Database: Create shared draft record
        API->>Database: Update stage: "generating_content"

        par Parallel Generation
            API->>BAML: GenerateEmailDraft
            and
            API->>BAML: GenerateTwitterThread
            and
            API->>BAML: GenerateLinkedInPost
        end

        par Update draft as content arrives
            BAML-->>API: Email content
            API->>Database: Update draft.email_draft
            and
            BAML-->>API: Twitter content
            API->>Database: Update draft.x_draft
            and
            BAML-->>API: LinkedIn content
            API->>Database: Update draft.linkedin_draft
        end

        Database->>Supabase: Real-time updates
        Supabase-->>Frontend: Draft updates
    end

    API->>Database: Update status: "ready"
    Frontend->>Frontend: Show completed state
```

### Draft Iteration - Refining Content with User Feedback

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant BackgroundTasks
    participant BAML
    participant Database
    participant Supabase

    User->>Frontend: Edit draft content
    User->>Frontend: Add feedback & click "Apply with AI"
    Frontend->>API: POST /videos/{id}/refine-content

    Note over API: Request includes:
    Note over API: - content_type (email/x/linkedin)
    Note over API: - feedback text
    Note over API: - current_draft content

    API->>API: Validate video & draft exist
    API->>Database: Create placeholder draft (preserves other content)
    API->>BackgroundTasks: Queue refine_content_background_task
    API-->>Frontend: 200 OK (immediate response)

    Note over BackgroundTasks: Background Refinement

    BackgroundTasks->>Database: Get video summary & transcript
    BackgroundTasks->>BackgroundTasks: Convert to BAML types

    alt Email Refinement
        BackgroundTasks->>BAML: RefineEmailDraft(current, feedback, context)
        BAML->>BAML: Analyze feedback
        BAML->>BAML: Apply changes maintaining tone
        BAML-->>BackgroundTasks: Refined email
        BackgroundTasks->>Database: Update draft.email_draft
    else Twitter Refinement
        BackgroundTasks->>BAML: RefineTwitterThread(current, feedback, context)
        BAML-->>BackgroundTasks: Refined thread
        BackgroundTasks->>Database: Update draft.x_draft
    else LinkedIn Refinement
        BackgroundTasks->>BAML: RefineLinkedInPost(current, feedback, context)
        BAML-->>BackgroundTasks: Refined post
        BackgroundTasks->>Database: Update draft.linkedin_draft
    end

    Database->>Supabase: Trigger real-time event
    Supabase-->>Frontend: WebSocket draft update
    Frontend->>Frontend: Update displayed content
    Frontend->>User: Show refined draft

    opt Title Generation
        User->>Frontend: Click "Generate Title with AI"
        Frontend->>API: POST /videos/{id}/generate-title
        API->>BackgroundTasks: Queue title generation
        BackgroundTasks->>BAML: GenerateYouTubeTitle(summary, transcript)
        BAML-->>BackgroundTasks: New title
        BackgroundTasks->>Database: Update video.title
        Database->>Supabase: Real-time update
        Supabase-->>Frontend: Title update
    end
```

### GitHub PR Creation - Manual Trigger with AI-Powered Content

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant GitHubService
    participant BAML
    participant Kit
    participant Supersonic
    participant GitHub

    User->>Frontend: Click "Create GitHub PR"
    Frontend->>Frontend: Show next episode form
    User->>Frontend: Enter next episode details
    Frontend->>API: POST /videos/{id}/create-github-pr

    Note over API: Request includes:
    Note over API: - next_episode_summary
    Note over API: - next_episode_luma_link

    API->>API: Validate required data exists
    API->>GitHubService: create_content_pr(video_data)

    rect rgb(240, 240, 250)
        Note over GitHubService: Determine Episode Path
        GitHubService->>Kit: Get repository file tree
        Kit->>GitHub: Fetch repo structure
        GitHub-->>Kit: File/folder list
        Kit-->>GitHubService: Existing episode folders

        GitHubService->>BAML: DetermineEpisodePath(title, date, folders)
        BAML->>BAML: Match date or topic
        BAML->>BAML: Or generate new path
        BAML-->>GitHubService: episode_path & is_new flag
    end

    rect rgb(250, 240, 240)
        Note over GitHubService: Generate Episode README
        GitHubService->>BAML: Get ExampleEpisodeReadme template

        opt If episode exists
            GitHubService->>Kit: Get existing README
            Kit-->>GitHubService: Current content
        end

        GitHubService->>BAML: GenerateEpisodeReadme(details)
        BAML->>BAML: Follow exact template format
        BAML->>BAML: Write Core Architecture section
        BAML-->>GitHubService: Formatted README
    end

    rect rgb(240, 250, 240)
        Note over GitHubService: Update Root README
        GitHubService->>Kit: Get current root README
        Kit-->>GitHubService: README content

        GitHubService->>BAML: GenerateRootReadmeUpdate(current, new_episode)
        BAML->>BAML: Move Next Session → Past Sessions
        BAML->>BAML: Add new episode entry
        BAML->>BAML: Update Next Session details
        BAML-->>GitHubService: Updated README
    end

    rect rgb(250, 250, 240)
        Note over GitHubService: Create Pull Request
        GitHubService->>Supersonic: create_pr_from_multiple_contents
        Note over Supersonic: Files to commit:
        Note over Supersonic: - {episode_path}/README.md
        Note over Supersonic: - README.md (root)

        Supersonic->>GitHub: Create branch
        Supersonic->>GitHub: Commit files
        Supersonic->>GitHub: Open PR
        GitHub-->>Supersonic: PR URL
        Supersonic-->>GitHubService: PR details
    end

    GitHubService-->>API: PR URL
    API->>Database: Update video.github_pr_url
    API-->>Frontend: Success response
    Frontend->>User: Show PR link
```

### Email Push to Loops - Future Integration

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant LoopsService
    participant LoopsAPI
    participant Database

    Note over User: Future Implementation

    User->>Frontend: Click "Push to Loops"
    Frontend->>API: POST /videos/{id}/push-to-loops

    API->>Database: Get latest email draft
    API->>LoopsService: send_campaign(email_content)

    LoopsService->>LoopsService: Format for Loops API
    LoopsService->>LoopsAPI: Create campaign
    LoopsAPI-->>LoopsService: Campaign ID

    LoopsService->>LoopsAPI: Schedule send
    LoopsAPI-->>LoopsService: Confirmation

    LoopsService-->>API: Success status
    API->>Database: Update email_sent_at
    API-->>Frontend: Success response
    Frontend->>User: Show confirmation
```

## Real-Time Updates

The system uses Supabase's real-time subscriptions to provide instant UI updates:

1. **Video Updates**: Status changes, processing stages, summary generation
2. **Draft Updates**: Content generation and refinement updates
3. **WebSocket Channels**: Dedicated channels per video for targeted updates
4. **Auto-reconnection**: Exponential backoff for connection reliability

## Key Design Decisions

1. **Parallel Processing**: Content generation runs concurrently for all platforms
2. **Streaming AI Responses**: Summary updates stream to UI in real-time
3. **Single Draft Model**: One draft record updated incrementally vs multiple versions
4. **Manual PR Trigger**: GitHub PRs require user action, not automatic
5. **Video Caching**: Downloaded Zoom videos cached locally to avoid re-downloads
6. **Smart Path Matching**: AI determines if episode already exists or needs new folder
7. **Background Tasks**: Long-running operations don't block API responses
