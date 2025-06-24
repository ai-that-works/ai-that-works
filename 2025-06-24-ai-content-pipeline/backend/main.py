from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

from models import (
    VideoImportRequest, DraftUpdateRequest, FeedbackRequest,
    Video, Draft, Feedback,
    VideoImportResponse, VideoResponse, SummaryResponse, 
    DraftsListResponse, DraftSaveResponse, FeedbackResponse, StatusResponse
)
from database import db

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
for var in required_env_vars:
    if not os.getenv(var):
        print(f"WARNING: {var} environment variable not set")

@app.get("/")
async def root():
    return {"message": "AI Content Pipeline API"}

@app.post("/videos/import", status_code=status.HTTP_202_ACCEPTED, response_model=VideoImportResponse)
async def import_video(request: VideoImportRequest):
    """Queue Zoom download - returns video ID immediately"""
    video_id = str(uuid.uuid4())
    
    # Create video record
    video = Video(
        id=video_id,
        title=f"Zoom Meeting {request.zoom_meeting_id}",
        duration=3600,  # 1 hour
        status="processing",
        created_at=datetime.now()
    )
    
    try:
        await db.create_video(video)
        return VideoImportResponse(video_id=video_id, status="queued")
    except Exception as e:
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/videos/{video_id}/summarize", status_code=status.HTTP_202_ACCEPTED, response_model=StatusResponse)
async def trigger_summarize(video_id: str):
    """Trigger Gemini pipeline"""
    try:
        video = await db.get_video(video_id)
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
        
        # Simulate processing - update status and add sample summary points
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/videos/{video_id}/drafts", response_model=DraftSaveResponse)
async def save_drafts(video_id: str, request: DraftUpdateRequest):
    """Save edited drafts"""
    try:
        video = await db.get_video(video_id)
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
        
        draft_id = str(uuid.uuid4())
        
        # Create new draft
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)