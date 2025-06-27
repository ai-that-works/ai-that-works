# OAuth Setup Guide

## Google Cloud Console Setup for YouTube API

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "New Project" or use the project selector
3. Name: `ai-content-pipeline`
4. Click "Create"

### 2. Enable YouTube Data API
1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "YouTube Data API v3"
3. Click on it and press "Enable"

### 3. Create OAuth 2.0 Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. If prompted, configure OAuth consent screen first:
   - Choose "External" for user type
   - Fill in required fields:
     - App name: `AI Content Pipeline`
     - User support email: your email
     - Developer contact: your email
   - Add scopes: `https://www.googleapis.com/auth/youtube.upload`
   - Add test users if needed
4. Create OAuth 2.0 Client ID:
   - Application type: "Desktop application"
   - Name: `AI Content Pipeline Desktop`
   - Click "Create"

### 4. Download Credentials
1. Click the download button next to your newly created OAuth client
2. Save the JSON file as `google_credentials.json` in your backend directory
3. **NEVER commit this file to version control**

### 5. Required Scopes
- `https://www.googleapis.com/auth/youtube.upload` - Upload videos
- `https://www.googleapis.com/auth/youtube.readonly` - Read channel info

## Zoom API Setup

### 1. Create Zoom App
1. Go to [Zoom Marketplace](https://marketplace.zoom.us/)
2. Sign in with your Zoom account
3. Click "Develop" → "Build App"
4. Choose "Server-to-Server OAuth" app type
5. Fill in app details:
   - App name: `AI Content Pipeline`
   - Company name: Your company
   - Developer contact: your email

### 2. Get API Credentials
1. Go to your app's "App Credentials" page
2. Copy the following:
   - **Account ID**: Your Zoom account ID
   - **Client ID**: Your app's client ID
   - **Client Secret**: Your app's client secret
3. Add required scopes:
   - `meeting:read` - Read meeting details
   - `recording:read` - Access recordings

### 3. Environment Variables Setup
```bash
# Add to backend/.env
ZOOM_ACCOUNT_ID=your_account_id_here
ZOOM_CLIENT_ID=your_client_id_here
ZOOM_CLIENT_SECRET=your_client_secret_here
```

## OAuth Token Generation

Use the provided OAuth setup script to generate initial tokens:

```bash
cd backend
uv run python oauth_setup.py
```

This will:
1. Generate Google OAuth tokens for YouTube API access
2. Test Zoom API connection
3. Save tokens securely for backend use

## Security Best Practices

### Google Credentials
- Store `google_credentials.json` outside of version control
- Use environment variables for sensitive data
- Rotate credentials regularly
- Use service accounts for production

### Zoom Credentials
- Never expose client secrets in frontend code
- Use server-to-server OAuth for backend operations
- Store tokens securely with proper encryption
- Implement token refresh logic

## Troubleshooting

### Google OAuth Issues
- **Invalid client**: Verify credentials file path
- **Access denied**: Check OAuth consent screen configuration
- **Quota exceeded**: Monitor API usage in Google Cloud Console

### Zoom API Issues
- **Invalid credentials**: Verify Account ID, Client ID, and Client Secret
- **Insufficient permissions**: Check app scopes in Zoom Marketplace
- **Rate limiting**: Implement proper backoff strategies

## Testing OAuth Setup

```bash
# Test Google OAuth
cd backend
uv run python -c "from oauth_setup import test_google_auth; test_google_auth()"

# Test Zoom API
cd backend  
uv run python -c "from oauth_setup import test_zoom_auth; test_zoom_auth()"
```