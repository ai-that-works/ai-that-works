from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


# Request Models
class VideoImportRequest(BaseModel):
    zoom_meeting_id: str
    title: str
    thumbnail_url: str


# Structured content models
class EmailDraftContent(BaseModel):
    subject: str
    body: str
    call_to_action: str

class XDraftContent(BaseModel):
    tweets: List[str]
    hashtags: List[str]

class LinkedInDraftContent(BaseModel):
    content: str
    hashtags: List[str]

class DraftUpdateRequest(BaseModel):
    email_draft: Optional[EmailDraftContent] = None
    x_draft: Optional[XDraftContent] = None
    linkedin_draft: Optional[LinkedInDraftContent] = None


class FeedbackRequest(BaseModel):
    content: str

class ContentRefinementRequest(BaseModel):
    feedback: str
    content_type: str  # "email", "x", "linkedin"
    current_draft: Optional[Dict[str, Any]] = None

class TitleUpdateRequest(BaseModel):
    title: str


class CreateGitHubPRRequest(BaseModel):
    next_episode_summary: str
    next_episode_luma_link: str


# Response Models
class Video(BaseModel):
    id: str
    title: str
    duration: int  # seconds
    zoom_meeting_id: str
    youtube_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    processing_stage: str = "queued"  # "queued", "downloading", "uploading", "ready", "failed"
    status: str  # "processing", "ready", "failed"
    created_at: datetime
    summary_points: Optional[List[str]] = None  # Legacy field, kept for backwards compatibility
    summary: Optional[Dict[str, Any]] = None  # Rich summary data from BAML
    transcript: Optional[str] = None


class Draft(BaseModel):
    id: str
    video_id: str
    email_draft: Optional[EmailDraftContent] = None
    x_draft: Optional[XDraftContent] = None
    linkedin_draft: Optional[LinkedInDraftContent] = None
    created_at: datetime
    version: int


class Feedback(BaseModel):
    id: str
    draft_id: str
    content: str
    created_at: datetime


# Zoom Recording Models
class ZoomRecording(BaseModel):
    meeting_id: str
    meeting_title: str
    recording_id: str
    recording_type: str
    file_size: int
    recording_start: Optional[str] = None
    recording_end: Optional[str] = None
    download_url: Optional[str] = None
    file_extension: str
    status: str
    duration: Optional[int] = None


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


class TranscriptResponse(BaseModel):
    transcript: str


class ZoomRecordingsResponse(BaseModel):
    recordings: List[ZoomRecording]
    total_count: int


# Grouped Zoom Meeting Model
class ZoomMeetingRecordings(BaseModel):
    meeting_id: str
    meeting_title: str
    recording_start: str
    recording_end: str
    recordings: List[ZoomRecording]


class ZoomMeetingsResponse(BaseModel):
    meetings: List[ZoomMeetingRecordings]
    total_count: int


# Luma Event Models
class LumaEvent(BaseModel):
    event_id: str
    title: str
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None


class LumaEventsResponse(BaseModel):
    events: List[LumaEvent]