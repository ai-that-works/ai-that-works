from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict
import uuid
from datetime import datetime, timedelta
import os
import logging
import asyncio
import json
from pathlib import Path

from models import (
    VideoImportRequest,
    DraftUpdateRequest,
    FeedbackRequest,
    ContentRefinementRequest,
    CreateGitHubPRRequest,
    Video,
    Draft,
    Feedback,
    VideoImportResponse,
    VideoResponse,
    SummaryResponse,
    DraftsListResponse,
    DraftSaveResponse,
    FeedbackResponse,
    StatusResponse,
    ZoomRecording,
    ZoomMeetingRecordings,
    ZoomMeetingsResponse,
    TranscriptResponse,
    LumaEventsResponse,
)
from database import db
from zoom_client import zoom_client
from video_processor import video_processor
from luma_client import luma_client
from baml_client import types
from baml_client.async_client import b
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Content Pipeline API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Disk-based cache for next AI that works event
class NextEventCache:
    def __init__(self, ttl_hours: int = 6):
        self.ttl = timedelta(hours=ttl_hours)
        self.cache_dir = Path(".cache")
        self.cache_file = self.cache_dir / "next_ai_that_works_event.json"
        self.lock = asyncio.Lock()

        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(exist_ok=True)

    async def get(self) -> Optional[Dict]:
        async with self.lock:
            if not self.cache_file.exists():
                return None

            try:
                with open(self.cache_file, "r") as f:
                    cache_data = json.load(f)

                # Check if cache has expired
                cache_time = datetime.fromisoformat(cache_data["timestamp"])
                if datetime.now() - cache_time > self.ttl:
                    # Cache expired, remove file
                    self.cache_file.unlink()
                    return None

                return cache_data["data"]
            except (json.JSONDecodeError, KeyError, ValueError):
                # Invalid cache file, remove it
                self.cache_file.unlink()
                return None

    async def set(self, data: Dict):
        async with self.lock:
            cache_data = {"timestamp": datetime.now().isoformat(), "data": data}

            # Ensure directory exists (in case it was deleted)
            self.cache_dir.mkdir(exist_ok=True)

            with open(self.cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)

    async def clear(self):
        async with self.lock:
            if self.cache_file.exists():
                self.cache_file.unlink()


# Initialize cache
next_event_cache = NextEventCache(ttl_hours=6)

# Validate required environment variables
required_env_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    print(f"WARNING: Missing environment variables: {', '.join(missing_vars)}")


@app.get("/")
async def root():
    return {"message": "AI Content Pipeline API"}


@app.get("/luma/recent-events", response_model=LumaEventsResponse)
async def get_recent_luma_events():
    """Get the 3 most recent past Luma events"""
    try:
        # Since the client is simplified, we'll need to handle this differently
        # For now, return empty list since the method is private
        return LumaEventsResponse(events=[])
    except Exception as e:
        logger.error(f"Error fetching Luma events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/luma/clear-cache")
async def clear_luma_cache():
    """Clear the cached next AI that works event - useful for forcing a refresh"""
    await next_event_cache.clear()
    logger.info("Cleared next AI that works event cache")
    return {
        "status": "cache_cleared",
        "message": "Next AI that works event cache has been cleared",
    }


@app.get("/luma/next-ai-that-works-event")
async def get_next_ai_that_works_event():
    """Get the next upcoming AI that works event with caching"""
    try:
        # Check cache first
        cached_result = await next_event_cache.get()
        if cached_result is not None:
            logger.info("Returning cached next AI that works event")
            return cached_result

        # Fetch fresh data if cache miss or expired
        logger.info("Fetching fresh next AI that works event from Luma")
        event = await luma_client.fetch_next_upcoming_event()

        if event:
            result = {
                "found": True,
                "event": {
                    "event_id": event.event_id,
                    "title": event.title,
                    "description": event.description,
                    "url": event.url,
                    "start_at": event.start_at.isoformat() if event.start_at else None,
                    "end_at": event.end_at.isoformat() if event.end_at else None,
                    "thumbnail_url": event.thumbnail_url,
                },
            }
        else:
            result = {"found": False, "event": None}

        # Cache the result
        await next_event_cache.set(result)

        return result
    except Exception as e:
        logger.error(f"Error fetching next AI that works event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.put("/videos/{video_id}/title")
async def update_video_title(video_id: str, request: dict):
    """Update video title"""
    try:
        new_title = request.get("title")
        if not new_title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Title is required"
            )

        video = await db.get_video(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
            )

        await db.update_video(video_id, {"title": new_title})
        return StatusResponse(status="updated")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating video title: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/zoom/recordings/{meeting_id}/luma-match")
async def get_luma_match_for_zoom_recording(meeting_id: str):
    """Check if a Zoom recording has a matching Luma event"""
    try:
        # Check if Luma API key is configured
        if not luma_client.api_key:
            logger.warning("LUMA_API_KEY not configured - returning no match")
            return {
                "matched": False,
                "event": None,
                "error": "Luma API key not configured",
            }

        # Use the simplified Luma client method
        luma_event = luma_client.get_event_for_zoom_meeting(meeting_id)

        if luma_event:
            return {"matched": True, "event": luma_event}
        else:
            return {"matched": False, "event": None}

    except Exception as e:
        logger.error(f"Error matching Zoom recording to Luma event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post(
    "/videos/import",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=VideoImportResponse,
)
async def import_video(request: VideoImportRequest, background_tasks: BackgroundTasks):
    """Queue Zoom download - returns video ID immediately and starts full background processing pipeline"""
    video_id = str(uuid.uuid4())

    # Create video record
    video = Video(
        id=video_id,
        zoom_meeting_id=request.zoom_meeting_id,
        title=request.title,
        thumbnail_url=request.thumbnail_url,
        duration=3600,  # 1 hour
        status="processing",
        processing_stage="queued",
        created_at=datetime.now(),
    )

    try:
        await db.create_video(video)

        # Add background task for complete video processing pipeline
        background_tasks.add_task(
            complete_video_processing_pipeline, video_id, request.zoom_meeting_id
        )

        return VideoImportResponse(video_id=video_id, status="queued")
    except Exception as e:
        print(f"Error creating video: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


async def complete_video_processing_pipeline(video_id: str, zoom_meeting_id: str):
    """Complete background processing pipeline: download video + upload to YouTube + auto-summarize + generate content"""
    try:
        print(f"🚀 Starting complete processing pipeline for video {video_id}")

        # Step 1: Process video (download, upload to YouTube, get transcript)
        await video_processor.process_video(video_id, zoom_meeting_id)

        # Step 2: Get the updated video with transcript
        video = await db.get_video(video_id)
        if not video:
            print(f"❌ Video {video_id} not found after processing")
            return

        # Step 3: Auto-trigger summarization if transcript is available
        if video.transcript:
            print(f"🧠 Auto-triggering summarization for video {video_id}")
            await process_video_summary(video_id, video.transcript, video.title)
        else:
            print(
                f"⚠️ No transcript available for video {video_id}, skipping auto-summarization"
            )

        print(f"✅ Complete processing pipeline finished for video {video_id}")

    except Exception as e:
        print(f"❌ Error in complete processing pipeline for video {video_id}: {e}")
        import traceback

        traceback.print_exc()
        # Update video status to failed
        await db.update_video(
            video_id, {"status": "failed", "processing_stage": "pipeline_failed"}
        )


@app.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str):
    """Get video details + drafts"""
    try:
        video = await db.get_video(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
            )

        video_drafts = await db.get_drafts_by_video(video_id)
        return VideoResponse(video=video, drafts=video_drafts)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting video {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post(
    "/videos/{video_id}/summarize",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=StatusResponse,
)
async def trigger_summarize(video_id: str, background_tasks: BackgroundTasks):
    """Trigger BAML summarization pipeline"""
    try:
        video = await db.get_video(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
            )

        if not video.transcript:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Video transcript not available for summarization",
            )

        # Add background task for summarization
        background_tasks.add_task(
            process_video_summary, video_id, video.transcript, video.title
        )

        # Update status to processing with detailed stage
        await db.update_video(
            video_id, {"status": "processing", "processing_stage": "summarizing"}
        )
        return StatusResponse(status="summarization started")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error triggering summarize for video {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


async def process_video_summary(
    video_id: str, transcript: str, title: Optional[str] = None
):
    """Background task to process video summary and generate content using BAML with parallel processing"""
    try:
        print(f"🚀 Starting BAML summarization for video {video_id}")

        # Step 1: Generate video summary FIRST
        stream = b.stream.SummarizeVideo(transcript=transcript, title=title)
        async for video_summary in stream:
            summary_data = video_summary.model_dump(mode="json")
            summary_data["generated_at"] = datetime.now().isoformat()
            await db.update_video(
                video_id,
                {
                    "summary": summary_data,
                    "summary_points": video_summary.bullet_points,
                    "processing_stage": "summarizing",
                },
            )
        video_summary = await stream.get_final_response()
        print(f"✅ BAML summarization completed for video {video_id}")

        # Step 2: Save summary to DB immediately and delete prior drafts
        summary_data = video_summary.model_dump(mode="json")
        summary_data["generated_at"] = datetime.now().isoformat()

        # Delete all existing drafts for this video (fresh start)
        print(f"🗑️ Deleting all existing drafts for video {video_id}")
        await db.delete_drafts_by_video(video_id)

        await db.update_video(
            video_id,
            {
                "summary": summary_data,
                "summary_points": video_summary.bullet_points,
                "processing_stage": "generating_content",
            },
        )
        print(f"💾 Summary saved for video {video_id}, UI updated immediately!")

        # Step 3: Create a single draft and update it as content generates
        print(f"🔄 Starting parallel content generation for video {video_id}")

        # Create a shared draft record first
        shared_draft_id = str(uuid.uuid4())
        initial_draft = Draft(
            id=shared_draft_id,
            video_id=video_id,
            email_draft=None,
            x_draft=None,
            linkedin_draft=None,
            created_at=datetime.now(),
            version=1,
        )

        await db.create_draft(initial_draft)
        print(f"📝 Created shared draft {shared_draft_id} for video {video_id}")

        # Create tasks for parallel execution that update the same draft
        import asyncio

        async def generate_and_update_email():
            try:
                print(f"📧 Generating email draft for video {video_id}")
                # Get updated video to use latest title
                updated_video = await db.get_video(video_id)
                structure: types.EmailStructure = await b.GetEmailBulletPoints(
                    summary=video_summary,
                    transcript=transcript,
                    video_title=updated_video.title if updated_video else title,
                )

                email_draft = await b.DraftEmail(
                    summary=video_summary, structure=structure
                )

                # Update the shared draft with email content
                from models import EmailDraftContent

                email_draft_content = EmailDraftContent(
                    subject=email_draft.subject,
                    body=email_draft.body,
                    call_to_action="<none>",
                )

                await db.update_draft_field(
                    shared_draft_id, "email_draft", email_draft_content
                )
                print(
                    f"✅ Email content updated in shared draft {shared_draft_id} - UI will update in real-time!"
                )

            except Exception as e:
                print(f"❌ Error generating email draft: {e}")

        async def generate_and_update_x():
            try:
                print(f"🐦 Generating X thread for video {video_id}")
                # Get updated video to use latest title
                updated_video = await db.get_video(video_id)
                twitter_thread: types.TwitterThread = await b.GenerateTwitterThread(
                    summary=video_summary,
                    video_title=updated_video.title if updated_video else title,
                )

                # Update the shared draft with X content
                from models import XDraftContent

                x_draft_content = XDraftContent(
                    tweets=twitter_thread.tweets, hashtags=twitter_thread.hashtags
                )

                await db.update_draft_field(shared_draft_id, "x_draft", x_draft_content)
                print(
                    f"✅ X content updated in shared draft {shared_draft_id} - UI will update in real-time!"
                )

            except Exception as e:
                print(f"❌ Error generating X draft: {e}")

        async def generate_and_update_linkedin():
            try:
                print(f"💼 Generating LinkedIn post for video {video_id}")
                # Get updated video to use latest title
                updated_video = await db.get_video(video_id)
                linkedin_post: types.LinkedInPost = await b.GenerateLinkedInPost(
                    summary=video_summary,
                    video_title=updated_video.title if updated_video else title,
                )

                # Update the shared draft with LinkedIn content
                from models import LinkedInDraftContent

                linkedin_draft_content = LinkedInDraftContent(
                    content=linkedin_post.content, hashtags=linkedin_post.hashtags
                )

                await db.update_draft_field(
                    shared_draft_id, "linkedin_draft", linkedin_draft_content
                )
                print(
                    f"✅ LinkedIn content updated in shared draft {shared_draft_id} - UI will update in real-time!"
                )

            except Exception as e:
                print(f"❌ Error generating LinkedIn draft: {e}")

        # Execute all content generation in parallel
        await asyncio.gather(
            generate_and_update_email(),
            generate_and_update_x(),
            generate_and_update_linkedin(),
            return_exceptions=True,  # Don't fail if one content type fails
        )

        print(f"🎉 All content generation completed for video {video_id}")

        # Finalize video status
        await db.update_video(
            video_id, {"status": "ready", "processing_stage": "completed"}
        )
        print(f"✅ Video {video_id} processing completed successfully")

    except Exception as e:
        print(f"❌ Error processing summary for video {video_id}: {e}")
        # Update video status to failed
        await db.update_video(
            video_id, {"status": "failed", "processing_stage": "summary_failed"}
        )


@app.get("/videos/{video_id}/summary", response_model=SummaryResponse)
async def get_summary(video_id: str):
    """Get summary points"""
    try:
        video = await db.get_video(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
            )

        return SummaryResponse(summary_points=video.summary_points or [])
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting summary for video {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/videos/{video_id}/transcript", response_model=TranscriptResponse)
async def get_transcript(video_id: str):
    """Get video transcript"""
    try:
        video = await db.get_video(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
            )

        if not video.transcript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not available"
            )

        return TranscriptResponse(transcript=video.transcript)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting transcript for video {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/videos/{video_id}/drafts", response_model=DraftsListResponse)
async def list_drafts(video_id: str):
    """List draft history"""
    try:
        video = await db.get_video(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
            )

        video_drafts = await db.get_drafts_by_video(video_id)
        return DraftsListResponse(drafts=video_drafts)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error listing drafts for video {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/videos/{video_id}/drafts", response_model=DraftSaveResponse)
async def save_drafts(video_id: str, request: DraftUpdateRequest):
    """Save edited drafts"""
    print(f"🎯 Save drafts endpoint called for video: {video_id}")
    print(f"📝 Request data: {request}")

    try:
        video = await db.get_video(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
            )

        draft_id = str(uuid.uuid4())

        # Get existing drafts to determine version number
        existing_drafts = await db.get_drafts_by_video(video_id)
        new_version = max([d.version for d in existing_drafts], default=0) + 1

        # Create new draft
        draft = Draft(
            id=draft_id,
            video_id=video_id,
            email_draft=request.email_draft,
            x_draft=request.x_draft,
            linkedin_draft=request.linkedin_draft,
            created_at=datetime.now(),
            version=new_version,
        )

        await db.create_draft(draft)
        print(f"✅ Draft saved successfully: {draft_id}")
        return DraftSaveResponse(draft_id=draft_id, status="saved")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error saving draft for video {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/drafts/{draft_id}/feedback", response_model=FeedbackResponse)
async def add_feedback(draft_id: str, request: FeedbackRequest):
    """Add feedback"""
    try:
        draft = await db.get_draft(draft_id)
        if not draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found"
            )

        feedback_id = str(uuid.uuid4())

        feedback = Feedback(
            id=feedback_id,
            draft_id=draft_id,
            content=request.content,
            created_at=datetime.now(),
        )

        await db.create_feedback(feedback)
        return FeedbackResponse(feedback_id=feedback_id, status="added")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error adding feedback for draft {draft_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/videos/{video_id}/refine-content", response_model=StatusResponse)
async def refine_content(
    video_id: str, request: ContentRefinementRequest, background_tasks: BackgroundTasks
):
    """Refine content based on user feedback using BAML - returns immediately, processes in background"""
    print(f"🎯 Content refinement called for video: {video_id}")
    print(f"📝 Feedback: {request.feedback}")
    print(f"🎨 Content type: {request.content_type}")

    try:
        # Validate video exists
        video = await db.get_video(video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
            )

        # Validate current draft content is provided
        if not request.current_draft:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current draft content is required",
            )

        # Validate content type
        if request.content_type not in ["email", "x", "linkedin"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid content_type. Must be 'email', 'x', or 'linkedin'",
            )

        # Create placeholder draft immediately for fast response
        draft_id = str(uuid.uuid4())
        existing_drafts = await db.get_drafts_by_video(video_id)
        new_version = max([d.version for d in existing_drafts], default=0) + 1

        # Get the latest draft to preserve other content types
        latest_draft = existing_drafts[0] if existing_drafts else None

        # Create placeholder draft preserving existing content
        from models import EmailDraftContent, XDraftContent, LinkedInDraftContent

        # Start with existing content from latest draft
        email_draft = latest_draft.email_draft if latest_draft else None
        x_draft = latest_draft.x_draft if latest_draft else None
        linkedin_draft = latest_draft.linkedin_draft if latest_draft else None

        # Set the content being refined to current version (will be updated in background)
        if request.content_type == "email":
            email_draft = EmailDraftContent(**request.current_draft)
        elif request.content_type == "x":
            x_draft = XDraftContent(**request.current_draft)
        elif request.content_type == "linkedin":
            linkedin_draft = LinkedInDraftContent(**request.current_draft)

        placeholder_draft = Draft(
            id=draft_id,
            video_id=video_id,
            email_draft=email_draft,
            x_draft=x_draft,
            linkedin_draft=linkedin_draft,
            created_at=datetime.now(),
            version=new_version,
        )

        await db.create_draft(placeholder_draft)
        print(f"✅ Placeholder draft created: {draft_id}")

        # Add background task to refine content
        background_tasks.add_task(
            refine_content_background_task,
            video_id,
            draft_id,
            request.content_type,
            request.feedback,
            request.current_draft,
        )

        print(f"🚀 Background refinement task started for draft {draft_id}")
        return StatusResponse(status="OK")

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error starting content refinement for video {video_id}: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


async def refine_content_background_task(
    video_id: str,
    draft_id: str,
    content_type: str,
    feedback: str,
    current_draft_data: dict,
):
    """Background task to refine content using BAML"""
    print(f"🔄 Starting background refinement for draft {draft_id} ({content_type})")

    try:
        # Get video and its data for context
        video = await db.get_video(video_id)
        if not video:
            print(f"❌ Video {video_id} not found during background refinement")
            return

        # Get video summary for context
        video_summary = None
        if hasattr(video, "summary") and video.summary:
            # Convert dict summary to BAML VideoSummary type
            video_summary = types.VideoSummary(
                bullet_points=video.summary.get("bullet_points", []),
                key_topics=video.summary.get("key_topics", []),
                main_takeaways=video.summary.get("main_takeaways", []),
            )
        elif video.summary_points:
            # Fallback to legacy format
            video_summary = types.VideoSummary(
                bullet_points=video.summary_points,
                key_topics=[],
                main_takeaways=[],
            )
        else:
            print(f"❌ No video summary available for video {video_id}")
            return

        # Refine content based on type using BAML
        refined_content = None

        if content_type == "email":
            current_email = types.EmailDraft(**current_draft_data)
            print("📧 Refining email content with BAML...")
            refined_content = await b.RefineEmailDraft(
                current_draft=current_email,
                feedback=feedback,
                summary=video_summary,
                transcript=video.transcript,
                video_title=video.title,
            )

            # Update the draft with refined email content
            from models import EmailDraftContent

            refined_email = EmailDraftContent(
                subject=refined_content.subject,
                body=refined_content.body,
                call_to_action="<none>",
            )
            await db.update_draft_field(draft_id, "email_draft", refined_email)

        elif content_type == "x":
            current_x = types.TwitterThread(**current_draft_data)
            print("🐦 Refining X thread content with BAML...")
            refined_content = await b.RefineTwitterThread(
                current_draft=current_x,
                feedback=feedback,
                summary=video_summary,
                transcript=video.transcript,
                video_title=video.title,
            )

            # Update the draft with refined X content
            from models import XDraftContent

            refined_x = XDraftContent(
                tweets=refined_content.tweets, hashtags=refined_content.hashtags
            )
            await db.update_draft_field(draft_id, "x_draft", refined_x)

        elif content_type == "linkedin":
            current_linkedin = types.LinkedInPost(**current_draft_data)
            print("💼 Refining LinkedIn post content with BAML...")
            refined_content = await b.RefineLinkedInPost(
                current_draft=current_linkedin,
                feedback=feedback,
                summary=video_summary,
                transcript=video.transcript,
                video_title=video.title,
            )

            # Update the draft with refined LinkedIn content
            from models import LinkedInDraftContent

            refined_linkedin = LinkedInDraftContent(
                content=refined_content.content, hashtags=refined_content.hashtags
            )
            await db.update_draft_field(draft_id, "linkedin_draft", refined_linkedin)

        print(
            f"✅ Background refinement completed for draft {draft_id} ({content_type})"
        )
        print("🔔 Real-time update will notify frontend of changes")

    except Exception as e:
        print(f"❌ Error in background refinement for draft {draft_id}: {e}")
        import traceback

        traceback.print_exc()


@app.post("/videos/{video_id}/create-github-pr", response_model=Dict[str, str])
async def create_github_pr(
    video_id: str, request: CreateGitHubPRRequest, background_tasks: BackgroundTasks
):
    """Manually trigger GitHub PR creation for a video"""
    logger.info(f"🚀 Starting GitHub PR creation for video {video_id}")
    logger.info(
        f"📝 Request data: next_episode_summary={request.next_episode_summary[:100]}..., luma_link={request.next_episode_luma_link}"
    )

    # Validate video exists and has required data
    logger.info(f"🔍 Fetching video {video_id} from database")
    video = await db.get_video(video_id)
    if not video:
        logger.error(f"❌ Video {video_id} not found in database")
        raise HTTPException(status_code=404, detail="Video not found")

    logger.info(f"✅ Found video: title={video.title}, created_at={video.created_at}")

    # Check required fields
    logger.info("🔍 Validating required video fields...")
    if not video.youtube_url:
        logger.error("❌ YouTube URL is missing")
        raise HTTPException(status_code=400, detail="YouTube URL is required")
    logger.info(f"✅ YouTube URL: {video.youtube_url}")

    if not video.transcript:
        logger.error("❌ Transcript is missing")
        raise HTTPException(status_code=400, detail="Transcript is required")
    logger.info(f"✅ Transcript available: {len(video.transcript)} characters")

    if not video.summary:
        logger.error("❌ Summary is missing")
        raise HTTPException(status_code=400, detail="Summary is required")
    logger.info(
        f"✅ Summary available with {len(video.summary.get('bullet_points', []))} bullet points"
    )

    # Validate request has next episode details
    logger.info("🔍 Validating next episode details...")
    if not request.next_episode_summary or not request.next_episode_luma_link:
        logger.error("❌ Next episode details are incomplete")
        raise HTTPException(status_code=400, detail="Next episode details are required")
    logger.info("✅ Next episode details validated")

    try:
        # Initialize GitHub service
        logger.info("🔧 Initializing GitHub PR service...")
        from github_pr_service import GitHubPRService

        github_service = GitHubPRService()
        logger.info(
            f"✅ GitHub service initialized - repo: {github_service.repo_owner}/{github_service.repo_name}"
        )

        # Extract YouTube video ID from URL
        logger.info(f"🎥 Extracting YouTube video ID from URL: {video.youtube_url}")
        youtube_video_id = (
            video.youtube_url.split("v=")[-1].split("&")[0]
            if "v=" in video.youtube_url
            else video.youtube_url.split("/")[-1]
        )
        logger.info(f"✅ Extracted YouTube video ID: {youtube_video_id}")
        logger.info(
            f"🖼️ Thumbnail URL: https://img.youtube.com/vi/{youtube_video_id}/0.jpg"
        )

        # Create PR
        logger.info("📤 Calling GitHub service to create PR...")
        logger.info(f"📅 Episode date: {video.created_at.strftime('%Y-%m-%d')}")
        pr_url = await github_service.create_content_pr(
            video_id=video.id,
            video_title=video.title,
            episode_date=video.created_at.strftime("%Y-%m-%d"),
            summary=video.summary,
            youtube_url=video.youtube_url,
            youtube_thumbnail_url=f"https://img.youtube.com/vi/{youtube_video_id}/0.jpg",
            transcript=video.transcript,
            zoom_recording_date=video.created_at,
            next_episode_summary=request.next_episode_summary,
            next_episode_luma_link=request.next_episode_luma_link,
        )
        logger.info(f"✅ PR created successfully: {pr_url}")

        # Update video with PR URL
        logger.info(f"💾 Updating video {video_id} with PR URL...")
        await db.update_video(video_id, {"github_pr_url": pr_url})
        logger.info("✅ Video updated with PR URL")

        logger.info(
            f"🎉 GitHub PR creation completed successfully for video {video_id}"
        )
        return {"pr_url": pr_url, "message": "GitHub PR created successfully"}

    except Exception as e:
        logger.error(f"❌ Failed to create GitHub PR for video {video_id}: {e}")
        logger.error("📊 Stack trace:", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test/supabase")
async def test_supabase():
    """Test Supabase connection and credentials"""
    try:
        # Test database connection by trying to get a count
        from database import db

        # Try a simple operation to test connection
        db.client.table("videos").select("count").execute()
        return {
            "status": "connected",
            "message": "Supabase credentials valid",
            "tables_accessible": True,
        }
    except Exception as e:
        print(f"Supabase test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Supabase connection failed: {str(e)}",
        )


@app.get("/test/zoom")
async def test_zoom():
    """Test Zoom API credentials"""
    zoom_account_id = os.getenv("ZOOM_ACCOUNT_ID")
    zoom_client_id = os.getenv("ZOOM_CLIENT_ID")
    zoom_client_secret = os.getenv("ZOOM_CLIENT_SECRET")

    if not zoom_account_id or not zoom_client_id or not zoom_client_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Zoom OAuth credentials not configured",
        )

    try:
        # Test the Zoom client
        recordings = zoom_client.get_recordings()
        return {
            "status": "configured",
            "message": "Zoom OAuth credentials valid",
            "recordings_count": len(recordings),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Zoom API test failed: {str(e)}",
        )


@app.get("/zoom/recordings", response_model=ZoomMeetingsResponse)
async def get_zoom_recordings(
    from_date: Optional[str] = None, to_date: Optional[str] = None, user_id: str = "me"
):
    """Fetch existing Zoom recordings, grouped by meeting"""
    try:
        recordings_data = zoom_client.get_recordings(
            user_id=user_id, from_date=from_date, to_date=to_date
        )
        # Group by meeting_id
        meetings = {}
        for rec in recordings_data:
            m_id = rec["meeting_id"]
            if m_id not in meetings:
                meetings[m_id] = {
                    "meeting_id": m_id,
                    "meeting_title": rec["meeting_title"],
                    "recording_start": rec["recording_start"],
                    "recording_end": rec["recording_end"],
                    "recordings": [],
                }
            meetings[m_id]["recordings"].append(ZoomRecording(**rec))
        meetings_list = [ZoomMeetingRecordings(**m) for m in meetings.values()]
        return ZoomMeetingsResponse(
            meetings=meetings_list, total_count=len(meetings_list)
        )
    except Exception as e:
        print(f"Error fetching Zoom recordings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch Zoom recordings: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
