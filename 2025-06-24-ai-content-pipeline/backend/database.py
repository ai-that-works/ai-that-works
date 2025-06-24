# Temporary database implementation - will be replaced by Infrastructure Agent
from typing import List, Optional, Dict, Any
from models import Video, Draft, Feedback

class DatabaseStub:
    def __init__(self):
        self.videos = {}
        self.drafts = {}
        self.feedback = {}
    
    async def create_video(self, video: Video) -> None:
        self.videos[video.id] = video
    
    async def get_video(self, video_id: str) -> Optional[Video]:
        return self.videos.get(video_id)
    
    async def update_video(self, video_id: str, updates: Dict[str, Any]) -> None:
        if video_id in self.videos:
            video = self.videos[video_id]
            for key, value in updates.items():
                if hasattr(video, key):
                    setattr(video, key, value)
    
    async def get_drafts_by_video(self, video_id: str) -> List[Draft]:
        return [d for d in self.drafts.values() if d.video_id == video_id]
    
    async def create_draft(self, draft: Draft) -> None:
        self.drafts[draft.id] = draft
    
    async def get_draft(self, draft_id: str) -> Optional[Draft]:
        return self.drafts.get(draft_id)
    
    async def create_feedback(self, feedback: Feedback) -> None:
        self.feedback[feedback.id] = feedback

# Global database instance
db = DatabaseStub()