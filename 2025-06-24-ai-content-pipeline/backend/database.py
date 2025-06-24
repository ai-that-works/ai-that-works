import os
from typing import List, Optional
from supabase import create_client, Client
from models import Video, Draft, Feedback


class Database:
    def __init__(self):
        self.client: Client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client"""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment")
        
        self.client = create_client(url, key)
    
    # Video operations
    async def create_video(self, video: Video) -> Video:
        """Create a new video record"""
        try:
            data = {
                "id": video.id,
                "title": video.title,
                "duration": video.duration,
                "youtube_url": video.youtube_url,
                "status": video.status,
                "created_at": video.created_at.isoformat(),
                "summary_points": video.summary_points
            }
            
            result = self.client.table("videos").insert(data).execute()
            return Video(**result.data[0])
        except Exception as e:
            raise Exception(f"Failed to create video: {str(e)}")
    
    async def get_video(self, video_id: str) -> Optional[Video]:
        """Get video by ID"""
        try:
            result = self.client.table("videos").select("*").eq("id", video_id).execute()
            if result.data:
                return Video(**result.data[0])
            return None
        except Exception as e:
            raise Exception(f"Failed to get video: {str(e)}")
    
    async def update_video(self, video_id: str, updates: dict) -> Optional[Video]:
        """Update video record"""
        try:
            result = self.client.table("videos").update(updates).eq("id", video_id).execute()
            if result.data:
                return Video(**result.data[0])
            return None
        except Exception as e:
            raise Exception(f"Failed to update video: {str(e)}")
    
    # Draft operations
    async def create_draft(self, draft: Draft) -> Draft:
        """Create a new draft record"""
        try:
            data = {
                "id": draft.id,
                "video_id": draft.video_id,
                "email_content": draft.email_content,
                "x_content": draft.x_content,
                "linkedin_content": draft.linkedin_content,
                "created_at": draft.created_at.isoformat(),
                "version": draft.version
            }
            
            result = self.client.table("drafts").insert(data).execute()
            return Draft(**result.data[0])
        except Exception as e:
            raise Exception(f"Failed to create draft: {str(e)}")
    
    async def get_drafts_by_video(self, video_id: str) -> List[Draft]:
        """Get all drafts for a video"""
        try:
            result = self.client.table("drafts").select("*").eq("video_id", video_id).execute()
            return [Draft(**item) for item in result.data]
        except Exception as e:
            raise Exception(f"Failed to get drafts: {str(e)}")
    
    async def get_draft(self, draft_id: str) -> Optional[Draft]:
        """Get draft by ID"""
        try:
            result = self.client.table("drafts").select("*").eq("id", draft_id).execute()
            if result.data:
                return Draft(**result.data[0])
            return None
        except Exception as e:
            raise Exception(f"Failed to get draft: {str(e)}")
    
    # Feedback operations
    async def create_feedback(self, feedback: Feedback) -> Feedback:
        """Create a new feedback record"""
        try:
            data = {
                "id": feedback.id,
                "draft_id": feedback.draft_id,
                "content": feedback.content,
                "created_at": feedback.created_at.isoformat()
            }
            
            result = self.client.table("feedback").insert(data).execute()
            return Feedback(**result.data[0])
        except Exception as e:
            raise Exception(f"Failed to create feedback: {str(e)}")
    
    async def get_feedback_by_draft(self, draft_id: str) -> List[Feedback]:
        """Get all feedback for a draft"""
        try:
            result = self.client.table("feedback").select("*").eq("draft_id", draft_id).execute()
            return [Feedback(**item) for item in result.data]
        except Exception as e:
            raise Exception(f"Failed to get feedback: {str(e)}")
    
    async def test_connection(self) -> bool:
        """Test database connection"""
        try:
            # Simple query to test connection
            self.client.table("videos").select("count", count="exact").execute()
            return True
        except Exception as e:
            print(f"Database connection test failed: {str(e)}")
            return False


# Global database instance
db = Database()