// Load environment variables from .env file
async function loadEnv() {
  try {
    const envFile = await Bun.file('.env').text();
    for (const line of envFile.split('\n')) {
      const [key, ...valueParts] = line.split('=');
      if (key && valueParts.length > 0) {
        const value = valueParts.join('=').trim();
        if (!process.env[key.trim()]) {
          process.env[key.trim()] = value;
        }
      }
    }
  } catch (error) {
    // .env file doesn't exist, continue with system environment variables
  }
}

interface ZoomToken {
  access_token: string;
  token_type: string;
  expires_in: number;
  scope: string;
  api_url: string;
  expires_at?: number;
}

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

class ZoomClient {
  private token?: ZoomToken;
  private tokenFile = './zoom_token.json';
  private ZOOM_ACCOUNT_ID: string;
  private ZOOM_CLIENT_ID: string;
  private ZOOM_CLIENT_SECRET: string;
  
  constructor() {
    this.ZOOM_ACCOUNT_ID = process.env.ZOOM_ACCOUNT_ID!;
    this.ZOOM_CLIENT_ID = process.env.ZOOM_CLIENT_ID!;
    this.ZOOM_CLIENT_SECRET = process.env.ZOOM_CLIENT_SECRET!;
  }
  
  async getAccessToken(): Promise<string> {
    // Check cached token
    if (await Bun.file(this.tokenFile).exists()) {
      const cached = await Bun.file(this.tokenFile).json() as ZoomToken;
      if (cached.expires_at && cached.expires_at > Date.now() / 1000) {
        return cached.access_token;
      }
    }
    
    // Get new token via OAuth
    const auth = Buffer.from(`${this.ZOOM_CLIENT_ID}:${this.ZOOM_CLIENT_SECRET}`).toString('base64');
    const response = await fetch(
      `https://zoom.us/oauth/token?grant_type=account_credentials&account_id=${this.ZOOM_ACCOUNT_ID}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${auth}`,
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    );
    
    if (!response.ok) {
      throw new Error(`Failed to get Zoom access token: ${response.status} - ${await response.text()}`);
    }
    
    const token = await response.json() as ZoomToken;
    token.expires_at = Date.now() / 1000 + token.expires_in;
    await Bun.write(this.tokenFile, JSON.stringify(token, null, 2));
    return token.access_token;
  }

  async fetchRecordings(fromDate?: Date, toDate?: Date): Promise<ZoomMeeting[]> {
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
      
      let token = await this.getAccessToken();
      let response = await fetch(
        `https://api.zoom.us/v2/users/me/recordings?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      if (response.status === 401) {
        // Token expired, refresh and retry
        this.token = undefined;
        token = await this.getAccessToken();
        response = await fetch(
          `https://api.zoom.us/v2/users/me/recordings?${params}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );
      }
      
      if (!response.ok) {
        throw new Error(`Failed to fetch Zoom recordings: ${response.status} - ${await response.text()}`);
      }
      
      const data = await response.json() as ZoomRecordingsResponse;
      meetings.push(...data.meetings);
      nextPageToken = data.next_page_token;
    } while (nextPageToken);
    
    return meetings;
  }
}

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

function validateEnvironment() {
  const required = ['ZOOM_ACCOUNT_ID', 'ZOOM_CLIENT_ID', 'ZOOM_CLIENT_SECRET'];
  const missing = required.filter(key => !process.env[key]);
  
  if (missing.length > 0) {
    console.error('Missing required environment variables:', missing.join(', '));
    console.error('Please set them in your .env file or environment');
    process.exit(1);
  }
}

async function main() {
  await loadEnv();
  validateEnvironment();
  
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (!command || command === '--help' || command === '-h') {
    console.log('Usage: bun run zoom.ts fetch-recent-recordings [--from YYYY-MM-DD] [--to YYYY-MM-DD]');
    process.exit(0);
  }
  
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
    
    // Ensure data directory exists
    await Bun.$`mkdir -p data`;
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

export { ZoomClient };