from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
from job_processor import create_video_processing_job, get_job_status, get_queue_status

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

@app.get("/")
async def root():
    return {"message": "AI Content Pipeline API"}

@app.post("/videos/import")
async def import_video(request: VideoImportRequest):
    """Queue Zoom download and AI processing - returns job ID immediately"""
    job_id = create_video_processing_job(request.zoom_meeting_id)
    return {"job_id": job_id, "meeting_id": request.zoom_meeting_id, "status": "queued"}

# Job status endpoints
@app.get("/jobs/{job_id}")
async def get_job_status_endpoint(job_id: str):
    """Get job status and results"""
    status = get_job_status(job_id)
    if "error" in status and status["error"] == "Job not found":
        raise HTTPException(status_code=404, detail="Job not found")
    return status

@app.get("/jobs")
async def get_queue_status_endpoint():
    """Get overall job queue status"""
    return get_queue_status()

# AI pipeline endpoints
@app.get("/jobs/{job_id}/video")
async def get_processed_video(job_id: str):
    """Get video processing results from completed job"""
    job_status = get_job_status(job_id)
    
    if "error" in job_status and job_status["error"] == "Job not found":
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job_status["status"] != "completed":
        return {"status": job_status["status"], "progress": job_status["progress"]}
    
    result = job_status["result"]
    if not result:
        raise HTTPException(status_code=500, detail="Job completed but no result available")
    
    return {
        "video": result["video"],
        "ai_content": result["ai_content"],
        "status": "completed"
    }

@app.get("/jobs/{job_id}/drafts")
async def get_ai_drafts(job_id: str):
    """Get AI-generated content drafts from completed job"""
    job_status = get_job_status(job_id)
    
    if "error" in job_status and job_status["error"] == "Job not found":
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job_status["status"] != "completed":
        return {"status": job_status["status"], "progress": job_status["progress"]}
    
    result = job_status["result"]
    if not result or "ai_content" not in result:
        raise HTTPException(status_code=500, detail="AI content not available")
    
    return result["ai_content"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 