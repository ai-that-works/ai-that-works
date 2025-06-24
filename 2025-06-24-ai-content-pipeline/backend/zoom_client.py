import os
import json
import requests
import base64
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ZoomClient:
    def __init__(self):
        self.base_url = "https://api.zoom.us/v2"
        self.access_token = self._get_access_token()
    
    def _get_access_token(self) -> str:
        """Get Zoom access token from stored credentials"""
        try:
            # First try to load from zoom_token.json
            if os.path.exists('zoom_token.json'):
                with open('zoom_token.json', 'r') as f:
                    token_data = json.load(f)
                return token_data['access_token']
            else:
                # Fallback to getting a new token
                return self._get_new_token()
        except Exception as e:
            print(f"Failed to get Zoom access token: {e}")
            return self._get_new_token()
    
    def _get_new_token(self) -> str:
        """Get new access token using server-to-server OAuth"""
        account_id = os.getenv('ZOOM_ACCOUNT_ID')
        client_id = os.getenv('ZOOM_CLIENT_ID')
        client_secret = os.getenv('ZOOM_CLIENT_SECRET')
        
        if not all([account_id, client_id, client_secret]):
            raise Exception("Missing Zoom environment variables")
        
        auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        
        response = requests.post(
            f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={account_id}",
            headers={"Authorization": f"Basic {auth_header}"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            
            # Save token for future use
            with open('zoom_token.json', 'w') as f:
                json.dump(token_data, f)
            
            return token_data['access_token']
        else:
            raise Exception(f"Failed to get server token: {response.text}")
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to Zoom API"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        print(f"Making {method} request to: {url}")
        print(f"Using access token: {self.access_token[:20]}...")
        
        response = requests.request(method, url, headers=headers, params=params)
        
        print(f"Response status: {response.status_code}")
        if response.status_code >= 400:
            print(f"Response text: {response.text[:500]}")
        
        if response.status_code == 401:
            print("Token expired, trying to refresh...")
            # Token expired, try to get a new token
            self.access_token = self._get_new_token()
            headers["Authorization"] = f"Bearer {self.access_token}"
            response = requests.request(method, url, headers=headers, params=params)
            
            print(f"After refresh - Response status: {response.status_code}")
            if response.status_code >= 400:
                print(f"After refresh - Response text: {response.text[:500]}")
        
        if response.status_code >= 400:
            raise Exception(f"Zoom API error: {response.status_code} - {response.text}")
        
        return response.json()
    
    def get_recordings(self, user_id: str = "me", from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of recordings for a user"""
        if not from_date:
            from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
        
        params = {
            "from": from_date,
            "to": to_date,
            "page_size": 100
        }
        
        recordings = []
        page_token = None
        
        while True:
            if page_token:
                params["next_page_token"] = page_token
            
            response = self._make_request("GET", f"/users/{user_id}/recordings", params)
            
            if "meetings" in response:
                for meeting in response["meetings"]:
                    if "recording_files" in meeting:
                        for recording in meeting["recording_files"]:
                            recordings.append({
                                "meeting_id": str(meeting["id"]),
                                "meeting_title": meeting.get("topic", "Untitled Meeting"),
                                "recording_id": str(recording["id"]),
                                "recording_type": recording.get("recording_type", "unknown"),
                                "file_size": recording.get("file_size", 0),
                                "recording_start": recording.get("recording_start"),
                                "recording_end": recording.get("recording_end"),
                                "download_url": recording.get("download_url"),
                                "file_extension": recording.get("file_extension", "mp4"),
                                "status": recording.get("status", "completed")
                            })
            
            page_token = response.get("next_page_token")
            if not page_token:
                break
        
        return recordings
    
    def get_recording_details(self, meeting_id: str, recording_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific recording"""
        response = self._make_request("GET", f"/meetings/{meeting_id}/recordings")
        
        for recording in response.get("recording_files", []):
            if recording["id"] == recording_id:
                return {
                    "meeting_id": str(meeting_id),
                    "recording_id": str(recording_id),
                    "meeting_title": response.get("topic", "Untitled Meeting"),
                    "recording_type": recording.get("recording_type", "unknown"),
                    "file_size": recording.get("file_size", 0),
                    "recording_start": recording.get("recording_start"),
                    "recording_end": recording.get("recording_end"),
                    "download_url": recording.get("download_url"),
                    "file_extension": recording.get("file_extension", "mp4"),
                    "status": recording.get("status", "completed"),
                    "duration": recording.get("duration", 0)
                }
        
        raise Exception(f"Recording {recording_id} not found in meeting {meeting_id}")

    def get_transcript(self, meeting_id: str) -> Optional[str]:
        """Get audio transcript for a specific meeting"""
        try:
            print(f"Getting recordings for meeting {meeting_id}...")
            response = self._make_request("GET", f"/meetings/{meeting_id}/recordings")
            
            print(f"Found {len(response.get('recording_files', []))} recording files")
            for i, recording in enumerate(response.get("recording_files", [])):
                recording_type = recording.get("recording_type", "unknown")
                print(f"Recording {i+1}: type={recording_type}, id={recording.get('id')}")
                
                if str(recording_type).lower() == "audio_transcript":
                    transcript_url = recording.get("download_url")
                    if transcript_url:
                        print(f"Found transcript URL: {transcript_url}")
                        # Include authorization headers for the download
                        headers = {
                            "Authorization": f"Bearer {self.access_token}",
                            "Content-Type": "application/json"
                        }
                        transcript_response = requests.get(transcript_url, headers=headers)
                        if transcript_response.status_code == 200:
                            transcript_text = transcript_response.text
                            print(f"Successfully downloaded transcript ({len(transcript_text)} characters)")
                            return transcript_text
                        else:
                            print(f"Failed to download transcript: {transcript_response.status_code} - {transcript_response.text[:200]}")
                            # Try without headers as fallback
                            transcript_response = requests.get(transcript_url)
                            if transcript_response.status_code == 200:
                                transcript_text = transcript_response.text
                                print(f"Successfully downloaded transcript without auth ({len(transcript_text)} characters)")
                                return transcript_text
                            else:
                                print(f"Failed to download transcript without auth: {transcript_response.status_code}")
            print(f"No transcript found for meeting {meeting_id}")
            return None
        except Exception as e:
            print(f"Error getting transcript for meeting {meeting_id}: {e}")
            return None

    def _get_chat_transcript(self, meeting_id: str, recording_id: str) -> Optional[str]:
        """Get chat transcript as fallback"""
        try:
            # Try to get chat messages from the meeting
            response = self._make_request("GET", f"/meetings/{meeting_id}/recordings")
            
            # Look for chat transcript in recording files
            for recording in response.get("recording_files", []):
                if recording["id"] == recording_id:
                    for file in recording.get("recording_files", []):
                        if file.get("recording_type") == "CHAT":
                            chat_url = file.get("download_url")
                            if chat_url:
                                chat_response = requests.get(chat_url)
                                if chat_response.status_code == 200:
                                    return chat_response.text
            
            return None
            
        except Exception as e:
            print(f"Error getting chat transcript: {e}")
            return None


# Global client instance
zoom_client = ZoomClient() 