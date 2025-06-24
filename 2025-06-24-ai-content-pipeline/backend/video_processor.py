import asyncio
import os
import tempfile
import requests
from typing import Optional
from datetime import datetime
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from database import db
from zoom_client import zoom_client


class VideoProcessor:
    def __init__(self):
        self.youtube_credentials = self._load_youtube_credentials()
    
    def _load_youtube_credentials(self) -> Optional[Credentials]:
        """Load YouTube API credentials from the existing OAuth setup"""
        try:
            # Use the tokens.json file created by oauth_setup_claude.py
            token_file = 'tokens.json'
            if not os.path.exists(token_file):
                print("WARNING: tokens.json not found. Run oauth_setup_claude.py first.")
                return None
            
            SCOPES = [
                'https://www.googleapis.com/auth/youtube.upload',
                'https://www.googleapis.com/auth/youtube.readonly'
            ]
            
            # Load credentials from the token file
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
            
            # Check if credentials are valid, refresh if needed
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        # Save refreshed credentials
                        with open(token_file, 'w') as token:
                            token.write(creds.to_json())
                    except Exception as e:
                        print(f"WARNING: Failed to refresh YouTube credentials: {e}")
                        return None
                else:
                    print("WARNING: YouTube credentials are invalid and cannot be refreshed.")
                    return None
            
            return creds
            
        except Exception as e:
            print(f"WARNING: Failed to load YouTube credentials: {e}")
            return None
    
    async def process_video(self, video_id: str, zoom_meeting_id: str):
        """Main processing pipeline: download Zoom recording and upload to YouTube"""
        try:
            # Update status to downloading
            await db.update_video(video_id, {
                "processing_stage": "downloading",
                "status": "processing"
            })
            
            # Download Zoom recording
            video_file_path = await self._download_zoom_recording(zoom_meeting_id)
            
            # Update status to uploading
            await db.update_video(video_id, {"processing_stage": "uploading"})
            
            # Upload to YouTube
            youtube_url = await self._upload_to_youtube(video_file_path, zoom_meeting_id)
            
            # Update final status
            await db.update_video(video_id, {
                "processing_stage": "ready",
                "status": "ready",
                "youtube_url": youtube_url
            })
            
            # Clean up temporary file
            if os.path.exists(video_file_path):
                os.remove(video_file_path)
                
        except Exception as e:
            print(f"Error processing video {video_id}: {e}")
            await db.update_video(video_id, {
                "processing_stage": "failed",
                "status": "failed"
            })
            raise
    
    async def _download_zoom_recording(self, zoom_meeting_id: str) -> str:
        """Download Zoom recording to temporary file"""
        try:
            # Get recording details from Zoom
            recordings = zoom_client.get_recordings()
            recording = None
            
            for rec in recordings:
                if rec["meeting_id"] == zoom_meeting_id:
                    recording = rec
                    break
            
            if not recording or not recording.get("download_url"):
                raise Exception(f"No downloadable recording found for meeting {zoom_meeting_id}")
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            temp_file_path = temp_file.name
            temp_file.close()
            
            # Download the file
            response = requests.get(recording["download_url"], stream=True)
            response.raise_for_status()
            
            with open(temp_file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return temp_file_path
            
        except Exception as e:
            raise Exception(f"Failed to download Zoom recording: {e}")
    
    async def _upload_to_youtube(self, video_file_path: str, zoom_meeting_id: str) -> Optional[str]:
        """Upload video to YouTube"""
        if not self.youtube_credentials:
            print("YouTube credentials not available, skipping upload")
            return None
        
        try:
            # Build YouTube service using the credentials from OAuth setup
            youtube = build('youtube', 'v3', credentials=self.youtube_credentials)
            
            # Prepare upload request
            body = {
                'snippet': {
                    'title': f'Zoom Meeting {zoom_meeting_id}',
                    'description': f'Recording from Zoom meeting {zoom_meeting_id}',
                    'tags': ['zoom', 'meeting', 'recording'],
                    'categoryId': '22'  # People & Blogs
                },
                'status': {
                    'privacyStatus': 'private'  # Start as private for safety
                }
            }
            
            # Create media upload
            media = MediaFileUpload(video_file_path, chunksize=-1, resumable=True)
            
            # Execute upload
            request = youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"Uploaded {int(status.progress() * 100)}%")
            
            video_id = response['id']
            return f"https://www.youtube.com/watch?v={video_id}"
            
        except HttpError as e:
            print(f"YouTube upload failed: {e}")
            return None
        except Exception as e:
            print(f"Error uploading to YouTube: {e}")
            return None


# Global processor instance
video_processor = VideoProcessor() 
