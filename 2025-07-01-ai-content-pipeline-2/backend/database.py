# Temporary database implementation - will be replaced by Infrastructure Agent
from datetime import datetime
from typing import List, Optional, Dict, Any
from models import Video, Draft, Feedback
import os
from supabase import create_client, Client
from dateutil.parser import parse as parse_datetime


class SupabaseDatabase:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            print("WARNING: Supabase credentials not configured. Using stub database.")
            print(
                "To use real Supabase database, set SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
            )
            self.client = None
            self._use_stub = True
        else:
            try:
                self.client: Client = create_client(supabase_url, supabase_key)
                self._use_stub = False
            except ImportError:
                print("WARNING: Supabase library not available. Using stub database.")
                self.client = None
                self._use_stub = True
            except Exception as e:
                print(
                    f"WARNING: Failed to initialize Supabase client: {e}. Using stub database."
                )
                self.client = None
                self._use_stub = True

    async def create_video(self, video: Video) -> None:
        """Create a new video record"""
        if self._use_stub:
            self._stub_videos[video.id] = video
            return

        video_data = {
            "id": video.id,
            "title": video.title,
            "duration": video.duration,
            "zoom_meeting_id": video.zoom_meeting_id,
            "youtube_url": video.youtube_url,
            "processing_stage": video.processing_stage,
            "status": video.status,
            "created_at": video.created_at.isoformat(),
            "summary_points": video.summary_points,
            "summary": video.summary,
            "transcript": video.transcript,
        }

        result = self.client.table("videos").insert(video_data).execute()
        if result.data is None:
            raise Exception("Failed to create video")

    async def get_video(self, video_id: str) -> Optional[Video]:
        """Get video by ID"""
        if self._use_stub:
            return self._stub_videos.get(video_id)

        result = self.client.table("videos").select("*").eq("id", video_id).execute()

        if not result.data:
            return None

        video_data = result.data[0]
        return Video(
            id=video_data["id"],
            title=video_data["title"],
            duration=video_data["duration"],
            zoom_meeting_id=video_data["zoom_meeting_id"],
            youtube_url=video_data.get("youtube_url"),
            processing_stage=video_data.get("processing_stage", "queued"),
            status=video_data["status"],
            created_at=parse_datetime(video_data["created_at"]),
            summary_points=video_data.get("summary_points"),
            summary=video_data.get("summary"),
            transcript=video_data.get("transcript"),
        )

    async def update_video(self, video_id: str, updates: Dict[str, Any]) -> None:
        """Update video fields"""
        if self._use_stub:
            if video_id in self._stub_videos:
                video = self._stub_videos[video_id]
                for key, value in updates.items():
                    if hasattr(video, key):
                        setattr(video, key, value)
            return

        # Convert datetime to ISO format if present
        update_data = {}
        for key, value in updates.items():
            if isinstance(value, datetime):
                update_data[key] = value.isoformat()
            else:
                update_data[key] = value

        result = (
            self.client.table("videos").update(update_data).eq("id", video_id).execute()
        )
        if result.data is None:
            raise Exception(f"Failed to update video {video_id}")

    async def get_drafts_by_video(self, video_id: str) -> List[Draft]:
        """Get all drafts for a video"""
        if self._use_stub:
            return [d for d in self._stub_drafts.values() if d.video_id == video_id]

        result = (
            self.client.table("drafts")
            .select("*")
            .eq("video_id", video_id)
            .order("created_at", desc=True)
            .execute()
        )

        drafts = []
        for draft_data in result.data:
            from models import EmailDraftContent, XDraftContent, LinkedInDraftContent

            email_draft = None
            if draft_data.get("email_draft"):
                email_draft = EmailDraftContent(**draft_data["email_draft"])

            x_draft = None
            if draft_data.get("x_draft"):
                x_draft = XDraftContent(**draft_data["x_draft"])

            linkedin_draft = None
            if draft_data.get("linkedin_draft"):
                linkedin_draft = LinkedInDraftContent(**draft_data["linkedin_draft"])

            drafts.append(
                Draft(
                    id=draft_data["id"],
                    video_id=draft_data["video_id"],
                    email_draft=email_draft,
                    x_draft=x_draft,
                    linkedin_draft=linkedin_draft,
                    created_at=parse_datetime(draft_data["created_at"]),
                    version=draft_data["version"],
                )
            )

        return drafts

    async def create_draft(self, draft: Draft) -> None:
        """Create a new draft"""
        if self._use_stub:
            self._stub_drafts[draft.id] = draft
            return

        draft_data = {
            "id": draft.id,
            "video_id": draft.video_id,
            "email_draft": draft.email_draft.model_dump()
            if draft.email_draft
            else None,
            "x_draft": draft.x_draft.model_dump() if draft.x_draft else None,
            "linkedin_draft": draft.linkedin_draft.model_dump()
            if draft.linkedin_draft
            else None,
            "created_at": draft.created_at.isoformat(),
            "version": draft.version,
        }

        result = self.client.table("drafts").insert(draft_data).execute()
        if result.data is None:
            raise Exception("Failed to create draft")

    async def get_draft(self, draft_id: str) -> Optional[Draft]:
        """Get draft by ID"""
        if self._use_stub:
            return self._stub_drafts.get(draft_id)

        result = self.client.table("drafts").select("*").eq("id", draft_id).execute()

        if not result.data:
            return None

        draft_data = result.data[0]
        from models import EmailDraftContent, XDraftContent, LinkedInDraftContent

        email_draft = None
        if draft_data.get("email_draft"):
            email_draft = EmailDraftContent(**draft_data["email_draft"])

        x_draft = None
        if draft_data.get("x_draft"):
            x_draft = XDraftContent(**draft_data["x_draft"])

        linkedin_draft = None
        if draft_data.get("linkedin_draft"):
            linkedin_draft = LinkedInDraftContent(**draft_data["linkedin_draft"])

        return Draft(
            id=draft_data["id"],
            video_id=draft_data["video_id"],
            email_draft=email_draft,
            x_draft=x_draft,
            linkedin_draft=linkedin_draft,
            created_at=parse_datetime(draft_data["created_at"]),
            version=draft_data["version"],
        )

    async def delete_draft(self, draft_id: str) -> None:
        """Delete draft by ID"""
        if self._use_stub:
            if draft_id in self._stub_drafts:
                del self._stub_drafts[draft_id]
            return

        result = self.client.table("drafts").delete().eq("id", draft_id).execute()
        if result.data is None:
            raise Exception(f"Failed to delete draft {draft_id}")

    async def delete_drafts_by_video(self, video_id: str) -> None:
        """Delete all drafts for a video"""
        if self._use_stub:
            # Remove all drafts for this video from stub storage
            to_delete = [
                draft_id
                for draft_id, draft in self._stub_drafts.items()
                if draft.video_id == video_id
            ]
            for draft_id in to_delete:
                del self._stub_drafts[draft_id]
            return

        result = self.client.table("drafts").delete().eq("video_id", video_id).execute()
        if result.data is None:
            raise Exception(f"Failed to delete drafts for video {video_id}")

    async def update_draft_field(
        self, draft_id: str, field_name: str, content: Any
    ) -> None:
        """Update a specific field in a draft (for parallel content generation)"""
        if self._use_stub:
            if draft_id in self._stub_drafts:
                draft = self._stub_drafts[draft_id]
                if hasattr(draft, field_name):
                    setattr(draft, field_name, content)
            return

        # Convert content to dict if it's a Pydantic model
        field_data = content.model_dump() if hasattr(content, "model_dump") else content

        update_data = {field_name: field_data}
        result = (
            self.client.table("drafts").update(update_data).eq("id", draft_id).execute()
        )
        if result.data is None:
            raise Exception(
                f"Failed to update draft field {field_name} for draft {draft_id}"
            )

    async def create_feedback(self, feedback: Feedback) -> None:
        """Create new feedback"""
        if self._use_stub:
            self._stub_feedback[feedback.id] = feedback
            return

        feedback_data = {
            "id": feedback.id,
            "draft_id": feedback.draft_id,
            "content": feedback.content,
            "created_at": feedback.created_at.isoformat(),
        }

        result = self.client.table("feedback").insert(feedback_data).execute()
        if result.data is None:
            raise Exception("Failed to create feedback")

    # Stub storage for fallback mode
    _stub_videos = {}
    _stub_drafts = {}
    _stub_feedback = {}


# Global database instance
db = SupabaseDatabase()
