from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

from models import (
    VideoImportRequest, DraftUpdateRequest, FeedbackRequest,
    Video, Draft, Feedback,
    VideoImportResponse, VideoResponse, SummaryResponse,
    DraftsListResponse, DraftSaveResponse, FeedbackResponse, StatusResponse,
    ZoomRecording, ZoomMeetingRecordings, ZoomMeetingsResponse
)
from database import db
from zoom_client import zoom_client

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Content Pipeline API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Validate required environment variables
required_env_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    print(f"WARNING: Missing environment variables: {', '.join(missing_vars)}")

@app.get("/")
async def root():
    return {"message": "AI Content Pipeline API"}

@app.post("/videos/import", status_code=status.HTTP_202_ACCEPTED, response_model=VideoImportResponse)
async def import_video(request: VideoImportRequest):
    """Queue Zoom download - returns video ID immediately"""
    video_id = str(uuid.uuid4())
    
    video = Video(
        id=video_id,
        zoom_meeting_id=request.zoom_meeting_id,
        title=f"Zoom Meeting {request.zoom_meeting_id}",
        duration=3600,
        status="processing",
        created_at=datetime.now()
    )
    
    try:
        await db.create_video(video)
        return VideoImportResponse(video_id=video_id, status="queued")
    except Exception as e:
        print(f"Error creating video: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str):
    """Get video details + drafts"""
    try:
        video = await db.get_video(video_id)
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
        
        video_drafts = await db.get_drafts_by_video(video_id)
        return VideoResponse(video=video, drafts=video_drafts)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting video {video_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/videos/{video_id}/summarize", status_code=status.HTTP_202_ACCEPTED, response_model=StatusResponse)
async def trigger_summarize(video_id: str):
    """Trigger Gemini pipeline"""
    try:
        video = await db.get_video(video_id)
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
        
        # Update status and add sample summary points
        updates = {
            "status": "processing",
            "summary_points": [
                "Key point 1: Introduction to AI content pipeline",
                "Key point 2: Benefits of automated content generation",
                "Key point 3: Best practices for implementation"
            ]
        }
        
        await db.update_video(video_id, updates)
        return StatusResponse(status="summarization started")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error triggering summarize for video {video_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/videos/{video_id}/summary", response_model=SummaryResponse)
async def get_summary(video_id: str):
    """Get summary points"""
    try:
        video = await db.get_video(video_id)
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
        
        return SummaryResponse(summary_points=video.summary_points or [])
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting summary for video {video_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/videos/{video_id}/drafts", response_model=DraftsListResponse)
async def list_drafts(video_id: str):
    """List draft history"""
    try:
        video = await db.get_video(video_id)
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
        
        video_drafts = await db.get_drafts_by_video(video_id)
        return DraftsListResponse(drafts=video_drafts)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error listing drafts for video {video_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/videos/{video_id}/drafts", response_model=DraftSaveResponse)
async def save_drafts(video_id: str, request: DraftUpdateRequest):
    """Save edited drafts"""
    try:
        video = await db.get_video(video_id)
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
        
        draft_id = str(uuid.uuid4())
        
        draft = Draft(
            id=draft_id,
            video_id=video_id,
            email_content=request.email_content,
            x_content=request.x_content,
            linkedin_content=request.linkedin_content,
            created_at=datetime.now(),
            version=1
        )
        
        await db.create_draft(draft)
        return DraftSaveResponse(draft_id=draft_id, status="saved")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error saving draft for video {video_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/drafts/{draft_id}/feedback", response_model=FeedbackResponse)
async def add_feedback(draft_id: str, request: FeedbackRequest):
    """Add feedback"""
    try:
        draft = await db.get_draft(draft_id)
        if not draft:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found")
        
        feedback_id = str(uuid.uuid4())
        
        feedback = Feedback(
            id=feedback_id,
            draft_id=draft_id,
            content=request.content,
            created_at=datetime.now()
        )
        
        await db.create_feedback(feedback)
        return FeedbackResponse(feedback_id=feedback_id, status="added")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error adding feedback for draft {draft_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/test/supabase")
async def test_supabase():
    """Test Supabase connection and credentials"""
    try:
        # Try a simple operation to test connection
        db.client.table("videos").select("count", count="exact").execute()
        return {
            "status": "connected",
            "message": "Supabase credentials valid",
            "tables_accessible": True
        }
    except Exception as e:
        print(f"Supabase test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Supabase connection failed: {str(e)}"
        )

@app.get("/test/zoom")
async def test_zoom():
    """Test Zoom API credentials"""
    zoom_api_key = os.getenv("ZOOM_API_KEY")
    zoom_api_secret = os.getenv("ZOOM_API_SECRET")
    
    if not zoom_api_key or not zoom_api_secret:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail="Zoom API credentials not configured")
    
    try:
        return {"status": "configured", "message": "Zoom API credentials found"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail=f"Zoom API test failed: {str(e)}")

@app.get("/zoom/recordings", response_model=ZoomMeetingsResponse)
async def get_zoom_recordings(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    user_id: str = "me"
):
    """Fetch existing Zoom recordings, grouped by meeting"""
    try:
        recordings_data = zoom_client.get_recordings(
            user_id=user_id,
            from_date=from_date,
            to_date=to_date
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
                    "recordings": []
                }
            meetings[m_id]["recordings"].append(ZoomRecording(**rec))
        meetings_list = [ZoomMeetingRecordings(**m) for m in meetings.values()]
        return ZoomMeetingsResponse(
            meetings=meetings_list,
            total_count=len(meetings_list)
        )
    except Exception as e:
        print(f"Error fetching Zoom recordings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch Zoom recordings: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)