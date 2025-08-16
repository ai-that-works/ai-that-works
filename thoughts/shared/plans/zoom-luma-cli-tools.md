# Zoom and Luma CLI Tools Implementation Plan

## Overview

Create two TypeScript CLI tools for fetching Zoom recordings and Luma events from their respective APIs, outputting formatted markdown files with clean asset links. These tools will be standalone Bun scripts that can be run independently and follow the patterns established in the 2025-07-01-ai-content-pipeline-2 Python implementations.

## Current State Analysis

The Python implementations in `2025-07-01-ai-content-pipeline-2/backend/` provide complete working examples:
- **Zoom**: OAuth 2.0 Server-to-Server authentication with token caching, paginated recording fetching
- **Luma**: API key authentication with calendar event fetching
- **Tools directory**: Empty Bun project with TypeScript configured and ready for development

### Key Discoveries:
- Zoom uses Server-to-Server OAuth (not user OAuth) with automatic token refresh: `2025-07-01-ai-content-pipeline-2/backend/zoom_client.py:33-58`
- Luma uses simple API key authentication: `2025-07-01-ai-content-pipeline-2/backend/luma_client.py:16-23`
- Both APIs return structured JSON that needs transformation to markdown
- Existing Python models define the data structures: `2025-07-01-ai-content-pipeline-2/backend/models.py:89-168`

## What We're NOT Doing

- NOT creating a web server or API endpoints
- NOT implementing video processing or downloading
- NOT integrating with BAML or AI systems
- NOT creating GitHub PR integrations
- NOT implementing event matching between Zoom and Luma
- NOT looking in any directories other than `2025-07-01-ai-content-pipeline-2` and `tools`

## Implementation Approach

Create two independent CLI tools using Bun's native capabilities, translating the Python implementations to TypeScript while maintaining the same authentication patterns and API interactions. Use environment variables for credentials and output markdown files with timestamped names.

## Phase 1: Core API Clients and Authentication

### Overview
Implement the base API client classes with authentication for both Zoom and Luma.

### Changes Required:

#### 1. Zoom OAuth Client
**File**: `tools/zoom.ts`
**Changes**: Create ZoomClient class with OAuth authentication

```typescript
// Environment variables
const ZOOM_ACCOUNT_ID = process.env.ZOOM_ACCOUNT_ID!;
const ZOOM_CLIENT_ID = process.env.ZOOM_CLIENT_ID!;
const ZOOM_CLIENT_SECRET = process.env.ZOOM_CLIENT_SECRET!;

interface ZoomToken {
  access_token: string;
  token_type: string;
  expires_in: number;
  scope: string;
  api_url: string;
  expires_at?: number;
}

class ZoomClient {
  private token?: ZoomToken;
  private tokenFile = './zoom_token.json';
  
  async getAccessToken(): Promise<string> {
    // Check cached token
    if (await Bun.file(this.tokenFile).exists()) {
      const cached = await Bun.file(this.tokenFile).json() as ZoomToken;
      if (cached.expires_at && cached.expires_at > Date.now() / 1000) {
        return cached.access_token;
      }
    }
    
    // Get new token via OAuth
    const auth = Buffer.from(`${ZOOM_CLIENT_ID}:${ZOOM_CLIENT_SECRET}`).toString('base64');
    const response = await fetch(
      `https://zoom.us/oauth/token?grant_type=account_credentials&account_id=${ZOOM_ACCOUNT_ID}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${auth}`,
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    );
    
    const token = await response.json() as ZoomToken;
    token.expires_at = Date.now() / 1000 + token.expires_in;
    await Bun.write(this.tokenFile, JSON.stringify(token, null, 2));
    return token.access_token;
  }
}
```

#### 2. Luma API Client
**File**: `tools/luma.ts`
**Changes**: Create LumaClient class with API key authentication

```typescript
const LUMA_API_KEY = process.env.LUMA_API_KEY!;
const LUMA_CALENDAR_ID = process.env.LUMA_CALENDAR_ID || 'cal-NQYQhHfQN7sg4BF';

class LumaClient {
  private baseUrl = 'https://public-api.lu.ma/public/v1';
  
  async fetchEvents(period: 'past' | 'future' = 'past'): Promise<LumaEvent[]> {
    const response = await fetch(
      `${this.baseUrl}/calendar/list-events?calendar_api_id=${LUMA_CALENDAR_ID}&period=${period}`,
      {
        headers: {
          'accept': 'application/json',
          'x-luma-api-key': LUMA_API_KEY
        }
      }
    );
    
    const data = await response.json();
    return data.entries || [];
  }
}
```

### Success Criteria:

#### Automated Verification:
- [x] TypeScript compilation passes: `bun run tools/zoom.ts --help`
- [x] TypeScript compilation passes: `bun run tools/luma.ts --help`
- [x] Environment variable validation works
- [x] Token file creation works for Zoom

#### Manual Verification:
- [x] Zoom OAuth token is successfully obtained
- [x] Luma API key authentication works
- [x] Both clients can make authenticated API calls

---

## Phase 2: Data Models and Type Definitions

### Overview
Define TypeScript interfaces for API responses and internal data structures.

### Changes Required:

#### 1. Zoom Data Models
**File**: `tools/zoom.ts`
**Changes**: Add interfaces for Zoom API responses

```typescript
interface ZoomRecordingFile {
  id: string;
  meeting_id: string;
  recording_type: string; // "shared_screen_with_speaker_view", "audio_transcript", etc.
  file_size: number;
  recording_start: string;
  recording_end: string;
  download_url?: string;
  file_extension: string;
  status: string;
}

interface ZoomMeeting {
  id: string;
  topic: string;
  start_time: string;
  duration: number;
  recording_files: ZoomRecordingFile[];
}

interface ZoomRecordingsResponse {
  meetings: ZoomMeeting[];
  next_page_token?: string;
}
```

#### 2. Luma Data Models
**File**: `tools/luma.ts`
**Changes**: Add interfaces for Luma API responses

```typescript
interface LumaEvent {
  api_id: string;
  event: {
    api_id: string;
    name: string;
    description?: string;
    start_at: string;
    end_at: string;
    url: string;
    cover_url?: string;
    timezone?: string;
    meeting_url?: string;
    zoom_meeting_url?: string;
  };
}
```

### Success Criteria:

#### Automated Verification:
- [x] TypeScript compilation with strict mode passes
- [x] No type errors in API response handling

#### Manual Verification:
- [x] API responses correctly map to interfaces
- [x] All optional fields are properly handled

---

## Phase 3: API Data Fetching

### Overview
Implement the core data fetching logic with pagination and date filtering.

### Changes Required:

#### 1. Zoom Recording Fetcher
**File**: `tools/zoom.ts`
**Changes**: Add method to fetch recordings with pagination

```typescript
class ZoomClient {
  async fetchRecordings(fromDate?: Date, toDate?: Date): Promise<ZoomMeeting[]> {
    const token = await this.getAccessToken();
    const meetings: ZoomMeeting[] = [];
    let nextPageToken: string | undefined;
    
    // Default to last 30 days if no dates provided
    const to = toDate || new Date();
    const from = fromDate || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
    
    do {
      const params = new URLSearchParams({
        from: from.toISOString().split('T')[0],
        to: to.toISOString().split('T')[0],
        page_size: '100',
        ...(nextPageToken && { next_page_token: nextPageToken })
      });
      
      const response = await fetch(
        `https://api.zoom.us/v2/users/me/recordings?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      if (response.status === 401) {
        // Token expired, refresh and retry
        this.token = undefined;
        const newToken = await this.getAccessToken();
        // Retry request...
      }
      
      const data = await response.json() as ZoomRecordingsResponse;
      meetings.push(...data.meetings);
      nextPageToken = data.next_page_token;
    } while (nextPageToken);
    
    return meetings;
  }
}
```

#### 2. Luma Event Fetcher with Filtering
**File**: `tools/luma.ts`
**Changes**: Add methods for recent and upcoming events

```typescript
class LumaClient {
  async fetchRecentAndUpcoming(): Promise<{past: LumaEvent[], future: LumaEvent[]}> {
    const [pastEvents, futureEvents] = await Promise.all([
      this.fetchEvents('past'),
      this.fetchEvents('future')
    ]);
    
    const now = new Date();
    
    // Sort past events by date descending (most recent first)
    const sortedPast = pastEvents
      .filter(e => new Date(e.event.start_at) < now)
      .sort((a, b) => new Date(b.event.start_at).getTime() - new Date(a.event.start_at).getTime())
      .slice(0, 10); // Last 10 events
    
    // Sort future events by date ascending (soonest first)
    const sortedFuture = futureEvents
      .filter(e => new Date(e.event.start_at) > now)
      .sort((a, b) => new Date(a.event.start_at).getTime() - new Date(b.event.start_at).getTime())
      .slice(0, 10); // Next 10 events
    
    return { past: sortedPast, future: sortedFuture };
  }
}
```

### Success Criteria:

#### Automated Verification:
- [x] Pagination logic handles multiple pages correctly
- [x] Date filtering produces correct date ranges
- [x] Token refresh on 401 works correctly

#### Manual Verification:
- [x] Fetches all available recordings within date range
- [x] Correctly sorts events by date
- [x] Handles API rate limits gracefully

---

## Phase 4: Markdown Output Formatting

### Overview
Create formatters that transform API data into the specified markdown formats.

### Changes Required:

#### 1. Zoom Markdown Formatter
**File**: `tools/zoom.ts`
**Changes**: Add markdown generation with asset links

```typescript
function formatZoomRecordings(meetings: ZoomMeeting[]): string {
  const lines: string[] = [];
  
  for (const meeting of meetings) {
    const startTime = new Date(meeting.start_time);
    const dateStr = startTime.toISOString().replace(/[:.]/g, '-').split('T')[0];
    const timeStr = startTime.toISOString().split('T')[1].split('.')[0].replace(/:/g, '-');
    
    lines.push(`### ${dateStr}-${timeStr}: ${meeting.topic}`);
    lines.push('');
    lines.push(`Duration: ${meeting.duration} minutes`);
    lines.push('');
    lines.push('Assets:');
    
    for (const file of meeting.recording_files) {
      const assetType = file.recording_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      if (file.download_url) {
        lines.push(`- [${assetType} (${file.file_extension.toUpperCase()})](${file.download_url})`);
      }
    }
    lines.push('');
  }
  
  return lines.join('\n');
}
```

#### 2. Luma Markdown Formatter
**File**: `tools/luma.ts`
**Changes**: Add markdown generation for events

```typescript
function formatLumaEvents(events: {past: LumaEvent[], future: LumaEvent[]}): string {
  const lines: string[] = [];
  
  lines.push('## Recent Events\n');
  for (const event of events.past) {
    lines.push(formatSingleEvent(event));
  }
  
  lines.push('## Upcoming Events\n');
  for (const event of events.future) {
    lines.push(formatSingleEvent(event));
  }
  
  return lines.join('\n');
}

function formatSingleEvent(event: LumaEvent): string {
  const startTime = new Date(event.event.start_at);
  const dateStr = startTime.toISOString().split('T')[0];
  const timeStr = startTime.toISOString().split('T')[1].split('.')[0];
  
  return `### ${dateStr}-${timeStr} - ${event.event.name}

**Description**: ${event.event.description || 'No description'}
**Date**: ${startTime.toLocaleString()}
**URL**: ${event.event.url}
**Image URL**: ${event.event.cover_url || 'No image'}
${event.event.zoom_meeting_url ? `**Zoom URL**: ${event.event.zoom_meeting_url}` : ''}

`;
}
```

### Success Criteria:

#### Automated Verification:
- [x] Markdown output is valid format
- [x] All required fields are included
- [x] Links are properly formatted

#### Manual Verification:
- [x] Output renders correctly in markdown viewers
- [x] Asset links are clickable and valid
- [x] Date formatting is consistent

---

## Phase 5: CLI Command Implementation

### Overview
Implement the command-line interface with proper argument handling.

### Changes Required:

#### 1. Zoom CLI Command
**File**: `tools/zoom.ts`
**Changes**: Add command parsing and execution

```typescript
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (command !== 'fetch-recent-recordings') {
    console.error('Usage: bun run zoom.ts fetch-recent-recordings [--from YYYY-MM-DD] [--to YYYY-MM-DD]');
    process.exit(1);
  }
  
  // Parse optional date arguments
  const fromIndex = args.indexOf('--from');
  const toIndex = args.indexOf('--to');
  const fromDate = fromIndex > -1 ? new Date(args[fromIndex + 1]) : undefined;
  const toDate = toIndex > -1 ? new Date(args[toIndex + 1]) : undefined;
  
  try {
    const client = new ZoomClient();
    console.log('Fetching Zoom recordings...');
    const meetings = await client.fetchRecordings(fromDate, toDate);
    
    const markdown = formatZoomRecordings(meetings);
    const filename = `data/${new Date().toISOString().split('T')[0]}-zoom-recordings.md`;
    
    await Bun.write(filename, markdown);
    console.log(`✓ Saved ${meetings.length} meetings to ${filename}`);
  } catch (error) {
    console.error('Error fetching Zoom recordings:', error);
    process.exit(1);
  }
}

if (import.meta.main) {
  main();
}
```

#### 2. Luma CLI Command
**File**: `tools/luma.ts`
**Changes**: Add command parsing and execution

```typescript
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (command !== 'fetch-recent-and-upcoming') {
    console.error('Usage: bun run luma.ts fetch-recent-and-upcoming');
    process.exit(1);
  }
  
  try {
    const client = new LumaClient();
    console.log('Fetching Luma events...');
    const events = await client.fetchRecentAndUpcoming();
    
    const markdown = formatLumaEvents(events);
    const filename = `data/${new Date().toISOString().split('T')[0]}-luma-recent-and-upcoming.md`;
    
    // Ensure data directory exists
    await Bun.$`mkdir -p data`;
    await Bun.write(filename, markdown);
    
    const total = events.past.length + events.future.length;
    console.log(`✓ Saved ${total} events to ${filename}`);
  } catch (error) {
    console.error('Error fetching Luma events:', error);
    process.exit(1);
  }
}

if (import.meta.main) {
  main();
}
```

### Success Criteria:

#### Automated Verification:
- [x] Commands execute without errors: `bun run tools/zoom.ts fetch-recent-recordings`
- [x] Commands execute without errors: `bun run tools/luma.ts fetch-recent-and-upcoming`
- [x] Data directory is created if it doesn't exist
- [x] Output files are created with correct names

#### Manual Verification:
- [x] Command-line arguments are parsed correctly
- [x] Error messages are helpful
- [x] Success messages show correct counts

---

## Phase 6: Error Handling and Environment Setup

### Overview
Add comprehensive error handling and environment variable validation.

### Changes Required:

#### 1. Environment Validation
**File**: `tools/zoom.ts` and `tools/luma.ts`
**Changes**: Add validation at startup

```typescript
function validateEnvironment() {
  const required = ['ZOOM_ACCOUNT_ID', 'ZOOM_CLIENT_ID', 'ZOOM_CLIENT_SECRET'];
  const missing = required.filter(key => !process.env[key]);
  
  if (missing.length > 0) {
    console.error('Missing required environment variables:', missing.join(', '));
    console.error('Please set them in your .env file or environment');
    process.exit(1);
  }
}
```

#### 2. .env.template File
**File**: `tools/.env.template`
**Changes**: Create template for environment variables

```bash
# Zoom API Credentials (Server-to-Server OAuth)
ZOOM_ACCOUNT_ID=your_zoom_account_id_here
ZOOM_CLIENT_ID=your_zoom_client_id_here
ZOOM_CLIENT_SECRET=your_zoom_client_secret_here

# Luma API Credentials
LUMA_API_KEY=your_luma_api_key_here
LUMA_CALENDAR_ID=cal-NQYQhHfQN7sg4BF
```

### Success Criteria:

#### Automated Verification:
- [x] Environment validation catches missing variables
- [x] Error messages are clear and actionable
- [x] Token refresh handles expired tokens correctly

#### Manual Verification:
- [x] Tools fail gracefully with helpful messages when credentials are missing
- [x] API errors are logged with context
- [x] Network errors are handled appropriately

---

## Testing Strategy

### Unit Tests:
- Test markdown formatting functions with sample data
- Test date parsing and filtering logic
- Test environment variable validation

### Integration Tests:
- Test actual API calls with real credentials
- Verify token caching and refresh for Zoom
- Test pagination handling with multiple pages

### Manual Testing Steps:
1. Set up environment variables from actual credentials
2. Run `bun run tools/zoom.ts fetch-recent-recordings` and verify output
3. Run `bun run tools/luma.ts fetch-recent-and-upcoming` and verify output
4. Check markdown files render correctly
5. Verify asset links in Zoom output are valid
6. Test with different date ranges for Zoom

## Performance Considerations

- Use Bun's native fetch API for optimal performance
- Cache Zoom OAuth tokens to minimize authentication calls
- Use Promise.all() for parallel API calls where possible
- Stream large responses if needed (though current data sizes are manageable)

## Migration Notes

- Copy environment variables from `2025-07-01-ai-content-pipeline-2/backend/.env` 
- Zoom token will be stored in `tools/zoom_token.json` (add to .gitignore)
- Output files go to `data/` directory (create if doesn't exist)

## References

- Original Zoom implementation: `2025-07-01-ai-content-pipeline-2/backend/zoom_client.py`
- Original Luma implementation: `2025-07-01-ai-content-pipeline-2/backend/luma_client.py`
- Data models: `2025-07-01-ai-content-pipeline-2/backend/models.py:89-168`
- Research document: `thoughts/shared/research/2025-08-16_11-07-26_zoom_luma_cli_scripts.md`