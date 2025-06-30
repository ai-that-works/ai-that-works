import os
import requests
import hashlib
from typing import Optional
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
        self.cache_dir = self._setup_cache_directory()
    
    def _setup_cache_directory(self) -> str:
        """Setup cache directory for downloaded videos"""
        cache_dir = os.path.join(os.getcwd(), "video_cache")
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            print(f"Created cache directory: {cache_dir}")
        return cache_dir
    
    def _get_cache_filename(self, zoom_meeting_id: str, recording_id: str) -> str:
        """Generate cache filename for a recording"""
        # Create a hash of the meeting and recording IDs for the filename
        hash_input = f"{zoom_meeting_id}_{recording_id}".encode()
        hash_value = hashlib.md5(hash_input).hexdigest()
        return os.path.join(self.cache_dir, f"{hash_value}.mp4")
    
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
        """Main processing pipeline: download Zoom recording, upload to YouTube, and trigger summarization"""
        try:
            # Update status to downloading
            await db.update_video(video_id, {
                "processing_stage": "downloading",
                "status": "processing"
            })
            
            # Download Zoom recording
            video_file_path = await self._download_zoom_recording(zoom_meeting_id)
            
            # Get transcript from Zoom
            transcript = await self._get_transcript(zoom_meeting_id)
            
            # Update status to uploading
            await db.update_video(video_id, {"processing_stage": "uploading"})
            
            # Upload to YouTube
            youtube_url = await self._upload_to_youtube(video_file_path, zoom_meeting_id)
            
            # Update status with transcript and YouTube URL
            update_data = {
                "processing_stage": "ready",
                "status": "ready",
                "youtube_url": youtube_url
            }
            
            if transcript:
                update_data["transcript"] = transcript
            
            await db.update_video(video_id, update_data)
            
            # Video processing completed - summarization will be triggered automatically by the import pipeline
            print(f"✅ Video processing completed for {video_id}")
            
            # Don't clean up the cached file - keep it for future use
            print(f"Video processing completed. Cached file: {video_file_path}")
                
        except Exception as e:
            print(f"Error processing video {video_id}: {e}")
            await db.update_video(video_id, {
                "processing_stage": "failed",
                "status": "failed"
            })
            raise
    
    async def _download_zoom_recording(self, zoom_meeting_id: str) -> str:
        """Download Zoom recording with caching"""
        try:
            print(f"Looking for recordings for meeting {zoom_meeting_id}...")
            
            # Get recording details from Zoom API
            recordings = zoom_client.get_recordings()
            recording = None
            
            # Find the meeting and get all its recordings
            meeting_recordings = []
            for rec in recordings:
                if rec["meeting_id"] == zoom_meeting_id:
                    meeting_recordings.append(rec)
            
            if not meeting_recordings:
                raise Exception(f"No recordings found for meeting {zoom_meeting_id}")
            
            print(f"Found {len(meeting_recordings)} recordings for meeting {zoom_meeting_id}:")
            for rec in meeting_recordings:
                print(f"  - {rec['recording_type']}: {rec.get('file_size', 0)} bytes")
            
            # Prioritize video recordings over audio-only
            # Order of preference: shared_screen_with_speaker_view > shared_screen > video_only > audio_only
            video_types = [
                'shared_screen_with_speaker_view(CC)',
                'shared_screen_with_speaker_view',
                'shared_screen',
                'video_only',
                'audio_only'
            ]
            
            for video_type in video_types:
                for rec in meeting_recordings:
                    if rec.get("recording_type") == video_type:
                        recording = rec
                        print(f"Selected recording type: {video_type}")
                        break
                if recording:
                    break
            
            if not recording:
                # Fallback to any recording with a download URL
                for rec in meeting_recordings:
                    if rec.get("download_url"):
                        recording = rec
                        print(f"Fallback to recording type: {rec.get('recording_type')}")
                        break
            
            if not recording:
                raise Exception(f"No downloadable recording found for meeting {zoom_meeting_id}")
            
            recording_id = recording.get("recording_id")
            if not recording_id:
                raise Exception(f"No recording ID found for meeting {zoom_meeting_id}")
            
            # Check if we have a cached version
            cache_filename = self._get_cache_filename(zoom_meeting_id, recording_id)
            if os.path.exists(cache_filename):
                print(f"Using cached video file: {cache_filename}")
                return cache_filename
            
            # Get the download URL from the recording details
            download_url = recording.get("download_url")
            if not download_url:
                raise Exception(f"No download URL found for recording {recording_id}")
            
            print(f"Downloading {recording.get('recording_type')} from: {download_url[:100]}...")
            
            # Download the file with proper authentication
            headers = {
                "Authorization": f"Bearer {zoom_client.access_token}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            # First try with authentication
            response = requests.get(download_url, headers=headers, stream=True)
            
            if response.status_code != 200:
                print(f"Download with auth failed ({response.status_code}), trying without auth...")
                # Try without authentication as fallback
                response = requests.get(download_url, stream=True)
            
            if response.status_code != 200:
                raise Exception(f"Failed to download video: HTTP {response.status_code}")
            
            # Download to cache file
            print(f"Downloading to cache file: {cache_filename}")
            with open(cache_filename, "wb") as f:
                total_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)
                        if total_size % (1024 * 1024) == 0:  # Print progress every MB
                            print(f"Downloaded {total_size // (1024 * 1024)} MB")
            
            print(f"Successfully downloaded video file: {cache_filename} ({total_size} bytes)")
            return cache_filename
            
        except Exception as e:
            print(f"Error in _download_zoom_recording: {e}")
            raise Exception(f"Failed to download Zoom recording: {e}")
    
    async def _get_transcript(self, zoom_meeting_id: str) -> Optional[str]:
        """Get transcript from Zoom recording"""
        try:
            transcript = zoom_client.get_transcript(zoom_meeting_id)
            if transcript:
                print(f"Successfully retrieved transcript for meeting {zoom_meeting_id}")
                return transcript
            else:
                print(f"No transcript available for meeting {zoom_meeting_id}")
                return None
        except Exception as e:
            print(f"Error getting transcript for meeting {zoom_meeting_id}: {e}")
            return None
    
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
