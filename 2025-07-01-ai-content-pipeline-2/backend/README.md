# AI Content Pipeline Backend

A FastAPI backend for the AI Content Pipeline that integrates with Supabase for data persistence and Zoom API for video recordings.

## Features

- **Supabase Integration**: Real-time database with PostgreSQL
- **Zoom API Integration**: Fetch and manage Zoom recordings
- **Video Processing**: Queue and track video processing status
- **Content Generation**: Generate email, X (Twitter), and LinkedIn content
- **Draft Management**: Save and version content drafts
- **Feedback System**: Collect feedback on generated content

## Setup

### 1. Environment Configuration

Copy the environment template and configure your variables:

```bash
cp env.template .env
```

Fill in your environment variables:

```env
# Supabase Configuration (Required)
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Zoom API Configuration (Required for Zoom features)
ZOOM_API_KEY=your_zoom_api_key
ZOOM_API_SECRET=your_zoom_api_secret

# Optional: Google/YouTube API Configuration
GOOGLE_CREDENTIALS_FILE=path/to/your/google_credentials.json
GOOGLE_TOKEN_FILE=path/to/your/tokens.json
```

### 2. Supabase Database Setup

#### Option A: Using the Setup Script (Recommended)

```bash
# Run the setup script
python setup_supabase.py
```

The script will:
- Verify your Supabase credentials
- Display the SQL schema to run
- Test the database connection

#### Option B: Manual Setup

1. Go to your Supabase dashboard
2. Navigate to the SQL Editor
3. Copy and paste the contents of `schema.sql`
4. Click "Run" to execute the schema

### 3. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 4. Run the Server

```bash
# Development mode with auto-reload
uv run main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Video Management

- `POST /videos/import` - Import a Zoom video
- `GET /videos/{video_id}` - Get video details and drafts
- `POST /videos/{video_id}/summarize` - Trigger video summarization
- `GET /videos/{video_id}/summary` - Get video summary points

### Draft Management

- `GET /videos/{video_id}/drafts` - List all drafts for a video
- `POST /videos/{video_id}/drafts` - Save a new draft

### Feedback

- `POST /drafts/{draft_id}/feedback` - Add feedback to a draft

### Zoom Integration

- `GET /zoom/recordings` - Fetch Zoom recordings

### Testing

- `GET /test/supabase` - Test Supabase connection
- `GET /test/zoom` - Test Zoom API credentials

## Database Schema

The application uses three main tables:

### Videos Table
- `id` (UUID) - Primary key
- `title` (TEXT) - Video title
- `duration` (INTEGER) - Duration in seconds
- `zoom_meeting_id` (TEXT) - Zoom meeting identifier
- `youtube_url` (TEXT) - Optional YouTube URL
- `status` (TEXT) - Processing status
- `created_at` (TIMESTAMP) - Creation timestamp
- `summary_points` (TEXT[]) - Array of summary points

### Drafts Table
- `id` (UUID) - Primary key
- `video_id` (UUID) - Foreign key to videos
- `email_content` (TEXT) - Email content
- `x_content` (TEXT) - X (Twitter) content
- `linkedin_content` (TEXT) - LinkedIn content
- `created_at` (TIMESTAMP) - Creation timestamp
- `version` (INTEGER) - Draft version number

### Feedback Table
- `id` (UUID) - Primary key
- `draft_id` (UUID) - Foreign key to drafts
- `content` (TEXT) - Feedback content
- `created_at` (TIMESTAMP) - Creation timestamp

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=.
```

### Code Formatting

```bash
# Format code
uv run black .
uv run isort .
```

### Type Checking

```bash
# Run type checker
uv run mypy .
```

## Troubleshooting

### Supabase Connection Issues

1. Verify your `SUPABASE_URL` and `SUPABASE_ANON_KEY` are correct
2. Check that your Supabase project is active
3. Ensure the database tables exist (run the schema)
4. Test connection with: `GET /test/supabase`

### Zoom API Issues

1. Verify your `ZOOM_API_KEY` and `ZOOM_API_SECRET` are correct
2. Check that your Zoom app has the necessary permissions
3. Test connection with: `GET /test/zoom`

### Common Errors

- **"Failed to create video"**: Check Supabase connection and table existence
- **"Video not found"**: Verify the video ID exists in the database
- **"Supabase connection failed"**: Check environment variables and network connectivity

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License.
