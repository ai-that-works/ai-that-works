"""
OAuth authentication framework for external services
"""

import os
from typing import Optional, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import json


class OAuthManager:
    """Manages OAuth flows for different services"""

    def __init__(self):
        self.google_credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE")
        self.google_token_file = os.getenv("GOOGLE_TOKEN_FILE")
        self.zoom_api_key = os.getenv("ZOOM_API_KEY")
        self.zoom_api_secret = os.getenv("ZOOM_API_SECRET")

        # OAuth scopes for different services
        self.google_scopes = [
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.readonly",
        ]

    def validate_env_variables(self) -> Dict[str, bool]:
        """Validate that required OAuth environment variables are set"""
        return {
            "google_credentials_file": bool(self.google_credentials_file),
            "google_token_file": bool(self.google_token_file),
            "zoom_api_key": bool(self.zoom_api_key),
            "zoom_api_secret": bool(self.zoom_api_secret),
        }

    # Google OAuth methods
    def get_google_auth_url(self, redirect_uri: str) -> str:
        """Get Google OAuth authorization URL"""
        if not self.google_credentials_file:
            raise ValueError("GOOGLE_CREDENTIALS_FILE not configured")

        flow = Flow.from_client_secrets_file(
            self.google_credentials_file, scopes=self.google_scopes
        )
        flow.redirect_uri = redirect_uri

        auth_url, _ = flow.authorization_url(prompt="consent")
        return auth_url

    def exchange_google_code(self, code: str, redirect_uri: str) -> Credentials:
        """Exchange Google OAuth code for credentials"""
        if not self.google_credentials_file:
            raise ValueError("GOOGLE_CREDENTIALS_FILE not configured")

        flow = Flow.from_client_secrets_file(
            self.google_credentials_file, scopes=self.google_scopes
        )
        flow.redirect_uri = redirect_uri

        flow.fetch_token(code=code)
        return flow.credentials

    def save_google_credentials(self, credentials: Credentials) -> bool:
        """Save Google credentials to file"""
        if not self.google_token_file:
            raise ValueError("GOOGLE_TOKEN_FILE not configured")

        try:
            with open(self.google_token_file, "w") as token_file:
                token_file.write(credentials.to_json())
            return True
        except Exception as e:
            print(f"Failed to save Google credentials: {e}")
            return False

    def load_google_credentials(self) -> Optional[Credentials]:
        """Load Google credentials from file"""
        if not self.google_token_file or not os.path.exists(self.google_token_file):
            return None

        try:
            with open(self.google_token_file, "r") as token_file:
                creds_data = json.load(token_file)

            credentials = Credentials.from_authorized_user_info(
                creds_data, self.google_scopes
            )

            # Refresh if expired
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                self.save_google_credentials(credentials)

            return credentials
        except Exception as e:
            print(f"Failed to load Google credentials: {e}")
            return None

    def get_youtube_service(self):
        """Get authenticated YouTube API service"""
        credentials = self.load_google_credentials()
        if not credentials:
            raise ValueError("No valid Google credentials found")

        return build("youtube", "v3", credentials=credentials)

    # Zoom OAuth methods (simplified - Zoom uses different OAuth flow)
    def validate_zoom_credentials(self) -> bool:
        """Validate Zoom API credentials are configured"""
        return bool(self.zoom_api_key and self.zoom_api_secret)

    def get_zoom_auth_headers(self) -> Dict[str, str]:
        """Get Zoom API authentication headers"""
        if not self.validate_zoom_credentials():
            raise ValueError("Zoom API credentials not configured")

        # This is a simplified example - real Zoom OAuth is more complex
        return {
            "Authorization": f"Bearer {self.zoom_api_key}",
            "Content-Type": "application/json",
        }

    # General OAuth status
    def get_oauth_status(self) -> Dict[str, Any]:
        """Get current OAuth status for all services"""
        google_creds = self.load_google_credentials()

        return {
            "google": {
                "configured": bool(self.google_credentials_file),
                "authenticated": bool(google_creds and not google_creds.expired),
                "expires_at": google_creds.expiry.isoformat()
                if google_creds and google_creds.expiry
                else None,
            },
            "zoom": {
                "configured": self.validate_zoom_credentials(),
                "authenticated": self.validate_zoom_credentials(),  # Simplified
            },
            "environment_variables": self.validate_env_variables(),
        }


# Global OAuth manager instance
oauth_manager = OAuthManager()
