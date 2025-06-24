from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# Request Models
class VideoImportRequest(BaseModel):
    zoom_meeting_id: str


class DraftUpdateRequest(BaseModel):
    email_content: str
    x_content: str
    linkedin_content: str


class FeedbackRequest(BaseModel):
    content: str


# Response Models
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


class Feedback(BaseModel):
    id: str
    draft_id: str
    content: str
    created_at: datetime


# API Response Models
class VideoImportResponse(BaseModel):
    video_id: str
    status: str


class VideoResponse(BaseModel):
    video: Video
    drafts: List[Draft]


class SummaryResponse(BaseModel):
    summary_points: List[str]


class DraftsListResponse(BaseModel):
    drafts: List[Draft]


class DraftSaveResponse(BaseModel):
    draft_id: str
    status: str


class FeedbackResponse(BaseModel):
    feedback_id: str
    status: str


class StatusResponse(BaseModel):
    status: str