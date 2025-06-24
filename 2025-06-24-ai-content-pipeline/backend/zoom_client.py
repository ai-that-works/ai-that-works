import os
import json
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class ZoomClient:
    def __init__(self):
        self.base_url = "https://api.zoom.us/v2"
        self.access_token = self._get_access_token()
    
    def _get_access_token(self) -> str:
        """Get Zoom access token from stored credentials"""
        try:
            if os.path.exists('zoom_token.json'):
                with open('zoom_token.json', 'r') as f:
                    token_data = json.load(f)
                return token_data['access_token']
            else:
                # Fallback to environment variables for server-to-server OAuth
                return self._get_server_token()
        except Exception as e:
            raise Exception(f"Failed to get Zoom access token: {e}")
    
    def _get_server_token(self) -> str:
        """Get access token using server-to-server OAuth"""
        import base64
        
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
        
        response = requests.request(method, url, headers=headers, params=params)
        
        if response.status_code == 401:
            # Token expired, try to refresh
            self.access_token = self._get_server_token()
            headers["Authorization"] = f"Bearer {self.access_token}"
            response = requests.request(method, url, headers=headers, params=params)
        
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


# Global client instance
zoom_client = ZoomClient() 