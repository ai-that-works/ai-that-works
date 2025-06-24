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
    zoom_meeting_id: str
    youtube_url: Optional[str] = None
    processing_stage: str = "queued"  # "queued", "downloading", "uploading", "ready", "failed"
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