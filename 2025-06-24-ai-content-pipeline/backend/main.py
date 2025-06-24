from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

app = FastAPI(title="AI Content Pipeline API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class VideoImportRequest(BaseModel):
    zoom_meeting_id: str

class Video(BaseModel):
    id: str
    title: str
    duration: int  # seconds
    youtube_url: Optional[str] = None
    status: str  # "processing", "ready", "failed"
    created_at: datetime
    summary_points: Optional[List[str]] = None

class Draft(BaseModel):
    id: str
    video_id: str
    email_content: str
    x_content: str
    linkedin_content: str
    created_at: datetime
    version: int

class DraftUpdateRequest(BaseModel):
    email_content: str
    x_content: str
    linkedin_content: str

class Feedback(BaseModel):
    id: str
    draft_id: str
    content: str
    created_at: datetime

class FeedbackRequest(BaseModel):
    content: str

# In-memory storage for stub data
videos_db = {}
drafts_db = {}
feedback_db = {}

@app.get("/")
async def root():
    return {"message": "AI Content Pipeline API"}

@app.post("/videos/import")
async def import_video(request: VideoImportRequest):
    """Queue Zoom download - returns video ID immediately"""
    video_id = str(uuid.uuid4())
    
    # Create stub video data
    videos_db[video_id] = Video(
        id=video_id,
        title=f"Zoom Meeting {request.zoom_meeting_id}",
        duration=3600,  # 1 hour
        status="processing",
        created_at=datetime.now()
    )
    
    return {"video_id": video_id, "status": "queued"}

@app.get("/videos/{video_id}")
async def get_video(video_id: str):
    """Get video details + drafts"""
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video = videos_db[video_id]
    video_drafts = [d for d in drafts_db.values() if d.video_id == video_id]
    
    return {
        "video": video,
        "drafts": video_drafts
    }

@app.post("/videos/{video_id}/summarize")
async def trigger_summarize(video_id: str):
    """Trigger Gemini pipeline"""
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Simulate processing
    videos_db[video_id].status = "processing"
    videos_db[video_id].summary_points = [
        "Key point 1: Introduction to AI content pipeline",
        "Key point 2: Benefits of automated content generation",
        "Key point 3: Best practices for implementation"
    ]
    
    return {"status": "summarization started"}

@app.get("/videos/{video_id}/summary")
async def get_summary(video_id: str):
    """Get summary points"""
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video = videos_db[video_id]
    return {"summary_points": video.summary_points or []}

@app.get("/videos/{video_id}/drafts")
async def list_drafts(video_id: str):
    """List draft history"""
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video_drafts = [d for d in drafts_db.values() if d.video_id == video_id]
    return {"drafts": video_drafts}

@app.post("/videos/{video_id}/drafts")
async def save_drafts(video_id: str, request: DraftUpdateRequest):
    """Save edited drafts"""
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    
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
    
    drafts_db[draft_id] = draft
    
    return {"draft_id": draft_id, "status": "saved"}

@app.post("/drafts/{draft_id}/feedback")
async def add_feedback(draft_id: str, request: FeedbackRequest):
    """Add feedback"""
    if draft_id not in drafts_db:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    feedback_id = str(uuid.uuid4())
    
    feedback = Feedback(
        id=feedback_id,
        draft_id=draft_id,
        content=request.content,
        created_at=datetime.now()
    )
    
    feedback_db[feedback_id] = feedback
    
    return {"feedback_id": feedback_id, "status": "added"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 