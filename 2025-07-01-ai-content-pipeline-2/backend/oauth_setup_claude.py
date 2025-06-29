#!/usr/bin/env python3
"""
OAuth Setup Script for AI Content Pipeline
Handles Google OAuth and Zoom API authentication setup
"""

import os
import json
import sys
import argparse
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        'ZOOM_ACCOUNT_ID',
        'ZOOM_CLIENT_ID',
        'ZOOM_CLIENT_SECRET'
    ]

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

def check_credential_files():
    """Check if required credential files exist"""
    missing_files = []

    # Check for Google credentials
    if not os.path.exists('google_credentials.json'):
        missing_files.append('google_credentials.json')

    if missing_files:
        print("❌ Missing credential files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n📋 Setup instructions:")
        print("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
        print("2. Create a new project or select existing one")
        print("3. Enable YouTube Data API v3:")
        print("   - Go to APIs & Services > Library")
        print("   - Search for 'YouTube Data API v3'")
        print("   - Click on it and press 'Enable'")
        print("4. Create OAuth 2.0 credentials:")
        print("   - Go to APIs & Services > Credentials")
        print("   - Click 'Create Credentials' > 'OAuth 2.0 Client IDs'")
        print("   - Choose 'Desktop application' as application type")
        print("   - Download the credentials JSON file")
        print("5. Rename it to 'google_credentials.json' and place it in the backend directory")
        return False

    print("✅ All required credential files found")
    return True

def setup_google_oauth():
    """Setup Google OAuth for YouTube API"""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        SCOPES = [
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube.readonly'
        ]

        creds = None
        token_file = 'tokens.json'

        # Load existing tokens with proper error handling
        if os.path.exists(token_file):
            try:
                creds = Credentials.from_authorized_user_file(token_file, SCOPES)
                # Validate that the token has required fields
                if not hasattr(creds, 'refresh_token') or not creds.refresh_token:
                    print("⚠️  Existing token file is missing refresh_token, will re-authenticate")
                    creds = None
            except Exception as e:
                print(f"⚠️  Invalid token file found: {e}")
                print("Removing invalid token file and re-authenticating...")
                try:
                    os.remove(token_file)
                except:
                    pass
                creds = None

        # If there are no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"⚠️  Token refresh failed: {e}")
                    creds = None

            if not creds or not creds.valid:
                # Check for credentials file
                creds_file = 'google_credentials.json'
                if not os.path.exists(creds_file):
                    print(f"❌ Google credentials file not found: {creds_file}")
                    print("Download it from Google Cloud Console and place it in the backend directory")
                    return False

                flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
                creds = flow.run_local_server(port=int(os.getenv('GOOGLE_AUTH_PORT', "3000")))

            # Save credentials for next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())

        # Test the connection
        youtube = build('youtube', 'v3', credentials=creds)
        request = youtube.channels().list(part='snippet', mine=True)
        response = request.execute()

        if response.get('items'):
            channel = response['items'][0]
            print(f"✅ Google OAuth setup successful! Connected to channel: {channel['snippet']['title']}")
            return True
        else:
            print("❌ No YouTube channel found for this account")
            return False

    except ImportError:
        print("❌ Google API libraries not installed. Run: uv add google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        return False
    except Exception as e:
        print(f"❌ Google OAuth setup failed: {e}")
        return False

def setup_zoom_oauth():
    """Setup Zoom API authentication"""
    try:
        import requests
        import base64

        account_id = os.getenv('ZOOM_ACCOUNT_ID')
        client_id = os.getenv('ZOOM_CLIENT_ID')
        client_secret = os.getenv('ZOOM_CLIENT_SECRET')

        # Get access token
        auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

        response = requests.post(
            f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={account_id}",
            headers={"Authorization": f"Basic {auth_header}"}
        )

        if response.status_code == 200:
            token_data = response.json()

            # Save token for backend use
            with open('zoom_token.json', 'w') as f:
                json.dump(token_data, f)

            # Test the connection
            access_token = token_data['access_token']
            test_response = requests.get(
                "https://api.zoom.us/v2/users/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            if test_response.status_code == 200:
                user_data = test_response.json()
                print(f"✅ Zoom API setup successful! Connected as: {user_data.get('email', 'Unknown')}")
                return True
            else:
                print(f"❌ Zoom API test failed: {test_response.text}")
                return False
        else:
            print(f"❌ Zoom OAuth failed: {response.text}")
            return False

    except ImportError:
        print("❌ Requests library not installed. Run: uv add requests")
        return False
    except Exception as e:
        print(f"❌ Zoom OAuth setup failed: {e}")
        return False

def test_google_auth():
    """Test Google OAuth connection"""
    if not os.path.exists('tokens.json'):
        print("❌ No Google tokens found. Run full setup first.")
        return False

    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        SCOPES = [
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube.readonly'
        ]

        try:
            creds = Credentials.from_authorized_user_file('tokens.json', SCOPES)
            # Validate that the token has required fields
            if not hasattr(creds, 'refresh_token') or not creds.refresh_token:
                print("❌ Token file is missing refresh_token field")
                return False
        except Exception as e:
            print(f"❌ Invalid token file: {e}")
            return False

        youtube = build('youtube', 'v3', credentials=creds)
        request = youtube.channels().list(part='snippet', mine=True)
        response = request.execute()

        if response.get('items'):
            print("✅ Google OAuth connection working")
            return True
        else:
            print("❌ Google OAuth connection failed")
            return False
    except Exception as e:
        print(f"❌ Google OAuth test failed: {e}")
        return False

def test_zoom_auth():
    """Test Zoom API connection"""
    if not os.path.exists('zoom_token.json'):
        print("❌ No Zoom tokens found. Run full setup first.")
        return False

    try:
        import requests

        with open('zoom_token.json', 'r') as f:
            token_data = json.load(f)

        access_token = token_data['access_token']
        response = requests.get(
            "https://api.zoom.us/v2/users/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code == 200:
            print("✅ Zoom API connection working")
            return True
        else:
            print("❌ Zoom API connection failed")
            return False
    except Exception as e:
        print(f"❌ Zoom API test failed: {e}")
        return False

def cleanup_invalid_tokens():
    """Remove invalid token files"""
    token_files = ['tokens.json', 'zoom_token.json']
    cleaned = []

    for token_file in token_files:
        if os.path.exists(token_file):
            try:
                # Try to validate the token file
                if token_file == 'tokens.json':
                    from google.oauth2.credentials import Credentials
                    SCOPES = [
                        'https://www.googleapis.com/auth/youtube.upload',
                        'https://www.googleapis.com/auth/youtube.readonly'
                    ]
                    creds = Credentials.from_authorized_user_file(token_file, SCOPES)
                    if not hasattr(creds, 'refresh_token') or not creds.refresh_token:
                        os.remove(token_file)
                        cleaned.append(token_file)
                elif token_file == 'zoom_token.json':
                    with open(token_file, 'r') as f:
                        data = json.load(f)
                    if 'access_token' not in data:
                        os.remove(token_file)
                        cleaned.append(token_file)
            except Exception:
                # If we can't read the file, it's probably invalid
                os.remove(token_file)
                cleaned.append(token_file)

    if cleaned:
        print(f"🧹 Cleaned up invalid token files: {', '.join(cleaned)}")

    return cleaned

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description='AI Content Pipeline OAuth Setup')
    parser.add_argument('--force', action='store_true', help='Force re-authentication even if tokens exist')
    parser.add_argument('--test-only', action='store_true', help='Only test existing connections')
    parser.add_argument('--cleanup', action='store_true', help='Clean up invalid token files and exit')

    args = parser.parse_args()

    print("🚀 AI Content Pipeline OAuth Setup")
    print("=" * 40)

    if not check_environment():
        sys.exit(1)

    # Clean up any invalid token files first
    cleanup_invalid_tokens()

    if args.cleanup:
        print("✅ Cleanup completed")
        return

    if args.test_only:
        print("\n🧪 Testing existing connections...")
        google_ok = test_google_auth()
        zoom_ok = test_zoom_auth()

        if google_ok and zoom_ok:
            print("\n✅ All connections working!")
        else:
            print("\n❌ Some connections failed. Run without --test-only to fix.")
            sys.exit(1)
        return

    # Check for required credential files (only for full setup)
    if not check_credential_files():
        sys.exit(1)

    if args.force:
        print("\n🔄 Force re-authentication mode...")
        # Remove existing token files
        for token_file in ['tokens.json', 'zoom_token.json']:
            if os.path.exists(token_file):
                os.remove(token_file)
                print(f"🗑️  Removed {token_file}")

    print("\n📝 Setting up Google OAuth...")
    google_success = setup_google_oauth()

    print("\n🔐 Setting up Zoom API...")
    zoom_success = setup_zoom_oauth()

    print("\n" + "=" * 40)

    if google_success and zoom_success:
        print("✅ All OAuth setups completed successfully!")
        print("\nNext steps:")
        print("1. Your tokens are saved in this directory")
        print("2. Add the token file paths to your .env file")
        print("3. Test your backend API endpoints")
    else:
        print("❌ Some OAuth setups failed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
