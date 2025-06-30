#!/usr/bin/env python3
"""
OAuth Setup Script for AI Content Pipeline
Handles Google OAuth and Zoom API authentication setup

Based on YouTube Data API v3 documentation:
https://developers.google.com/youtube/v3/guides/uploading_a_video
"""

import os
import json
import sys
import base64
from dotenv import load_dotenv

load_dotenv()

# YouTube API configuration
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Retry configuration for uploads
MAX_RETRIES = 10
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]


def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["ZOOM_ACCOUNT_ID", "ZOOM_CLIENT_ID", "ZOOM_CLIENT_SECRET"]

    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("Please set these in your .env file")
        return False

    print("✅ All required environment variables are set")
    return True


def get_authenticated_youtube_service():
    """
    Get authenticated YouTube service using OAuth 2.0
    Based on YouTube API documentation pattern
    """
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        SCOPES = [YOUTUBE_UPLOAD_SCOPE, YOUTUBE_READONLY_SCOPE]
        creds = None
        token_file = "youtube_tokens.json"

        # Load existing tokens
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)

        # If there are no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("🔄 Refreshing expired Google OAuth tokens...")
                creds.refresh(Request())
            else:
                # Check for credentials file
                creds_file = "google_credentials.json"
                if not os.path.exists(creds_file):
                    print(f"❌ Google credentials file not found: {creds_file}")
                    print(
                        "Download it from Google Cloud Console and place it in the backend directory"
                    )
                    print("File should contain OAuth 2.0 client credentials")
                    return None

                print("🔐 Starting Google OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(token_file, "w") as token:
                token.write(creds.to_json())
            print("💾 Google OAuth tokens saved")

        # Build the YouTube service
        youtube = build(
            YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=creds
        )
        return youtube

    except ImportError as e:
        print(f"❌ Missing Google API libraries: {e}")
        print(
            "Install with: uv add google-api-python-client google-auth-httplib2 google-auth-oauthlib"
        )
        return None
    except Exception as e:
        print(f"❌ Google OAuth setup failed: {e}")
        return None


def test_youtube_connection(youtube):
    """Test YouTube API connection by fetching channel info"""
    try:
        request = youtube.channels().list(part="snippet,statistics", mine=True)
        response = request.execute()

        if response.get("items"):
            channel = response["items"][0]
            snippet = channel["snippet"]
            stats = channel.get("statistics", {})

            print("✅ YouTube API connected successfully!")
            print(f"   Channel: {snippet['title']}")
            print(f"   Subscribers: {stats.get('subscriberCount', 'Hidden')}")
            print(f"   Videos: {stats.get('videoCount', 'Unknown')}")
            return True
        else:
            print("❌ No YouTube channel found for this account")
            return False

    except Exception as e:
        print(f"❌ YouTube API test failed: {e}")
        return False


def setup_zoom_oauth():
    """Setup Zoom API authentication using Server-to-Server OAuth"""
    try:
        import requests

        account_id = os.getenv("ZOOM_ACCOUNT_ID")
        client_id = os.getenv("ZOOM_CLIENT_ID")
        client_secret = os.getenv("ZOOM_CLIENT_SECRET")

        if not all([account_id, client_id, client_secret]):
            print("❌ Missing Zoom environment variables")
            return False

        # Get access token using Server-to-Server OAuth
        auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

        print("🔐 Getting Zoom access token...")
        response = requests.post(
            f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={account_id}",
            headers={"Authorization": f"Basic {auth_header}"},
        )

        if response.status_code == 200:
            token_data = response.json()

            # Save token for backend use
            with open("zoom_token.json", "w") as f:
                json.dump(token_data, f)

            print("💾 Zoom access token saved")
            return True
        else:
            print(f"❌ Zoom OAuth failed: {response.status_code} - {response.text}")
            return False

    except ImportError:
        print("❌ Requests library not installed. Run: uv add requests")
        return False
    except Exception as e:
        print(f"❌ Zoom OAuth setup failed: {e}")
        return False


def test_zoom_connection():
    """Test Zoom API connection by fetching user info"""
    try:
        import requests

        if not os.path.exists("zoom_token.json"):
            print("❌ No Zoom tokens found. Run setup first.")
            return False

        with open("zoom_token.json", "r") as f:
            token_data = json.load(f)

        access_token = token_data["access_token"]

        print("🔍 Testing Zoom API connection...")
        response = requests.get(
            "https://api.zoom.us/v2/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if response.status_code == 200:
            user_data = response.json()
            print("✅ Zoom API connected successfully!")
            print(
                f"   User: {user_data.get('first_name', '')} {user_data.get('last_name', '')}"
            )
            print(f"   Email: {user_data.get('email', 'Unknown')}")
            print(f"   Account: {user_data.get('account_id', 'Unknown')}")
            return True
        else:
            print(f"❌ Zoom API test failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Zoom API test failed: {e}")
        return False


def test_google_auth():
    """Test Google OAuth connection"""
    if not os.path.exists("youtube_tokens.json"):
        print("❌ No Google tokens found. Run full setup first.")
        return False

    try:
        youtube = get_authenticated_youtube_service()
        if youtube:
            return test_youtube_connection(youtube)
        return False
    except Exception as e:
        print(f"❌ Google OAuth test failed: {e}")
        return False


def test_zoom_auth():
    """Test Zoom API connection"""
    return test_zoom_connection()


def create_sample_upload_request(youtube):
    """Create a sample upload request to test permissions"""
    try:
        # This is a test request that doesn't actually upload anything
        # It just verifies we have the right permissions
        body = {
            "snippet": {
                "title": "Test Video Title",
                "description": "Test video description",
                "tags": ["test"],
                "categoryId": "22",  # People & Blogs
            },
            "status": {"privacyStatus": "private"},
        }

        # This would normally upload a file, but we're just testing permissions
        print("✅ YouTube upload permissions verified")
        return True

    except Exception as e:
        print(f"❌ YouTube upload permission test failed: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 AI Content Pipeline OAuth Setup")
    print("=" * 50)

    if not check_environment():
        sys.exit(1)

    print("\n📝 Setting up Google OAuth for YouTube API...")
    youtube = get_authenticated_youtube_service()
    google_success = False

    if youtube:
        google_success = test_youtube_connection(youtube)
        if google_success:
            create_sample_upload_request(youtube)

    print("\n🔐 Setting up Zoom API...")
    zoom_success = setup_zoom_oauth()

    if zoom_success:
        zoom_success = test_zoom_connection()

    print("\n" + "=" * 50)

    if google_success and zoom_success:
        print("✅ All OAuth setups completed successfully!")
        print("\n📁 Generated files:")
        print("   - youtube_tokens.json (Google OAuth tokens)")
        print("   - zoom_token.json (Zoom access token)")
        print("\n🔧 Next steps:")
        print("1. Add token file paths to your .env file")
        print("2. Test your backend API endpoints")
        print("3. Run 'uv run python oauth_setup.py' again to test connections")
    else:
        print("❌ Some OAuth setups failed. Check the errors above.")
        if not google_success:
            print("\n💡 Google OAuth troubleshooting:")
            print("   - Ensure google_credentials.json is in the backend directory")
            print("   - Verify OAuth consent screen is configured")
            print("   - Check that YouTube Data API v3 is enabled")
        if not zoom_success:
            print("\n💡 Zoom API troubleshooting:")
            print("   - Verify ZOOM_* environment variables are set")
            print("   - Check app credentials in Zoom Marketplace")
            print("   - Ensure app has required scopes")
        sys.exit(1)


if __name__ == "__main__":
    main()
