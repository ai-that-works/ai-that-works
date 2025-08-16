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
  event_image_url?: string; // Will be populated with the event-specific og:image
}

class LumaClient {
  private baseUrl = 'https://public-api.lu.ma/public/v1';
  private LUMA_API_KEY: string;
  private LUMA_CALENDAR_ID: string;
  
  constructor() {
    this.LUMA_API_KEY = process.env.LUMA_API_KEY!;
    this.LUMA_CALENDAR_ID = process.env.LUMA_CALENDAR_ID || 'cal-NQYQhHfQN7sg4BF';
  }

  private extractImageFromDescription(event: LumaEvent): string | undefined {
    const description = event.event.description_md || event.event.description || '';
    
    // Look for markdown image syntax: ![alt](url)
    const markdownImageMatch = description.match(/!\[.*?\]\((https?:\/\/[^\s\)]+)\)/);
    if (markdownImageMatch) {
      console.log(`✓ Found image in description (markdown): ${markdownImageMatch[1]}`);
      return markdownImageMatch[1];
    }
    
    // Look for direct image URLs in the description
    const directImageMatch = description.match(/(https?:\/\/[^\s]+\.(?:jpg|jpeg|png|gif|webp))/i);
    if (directImageMatch) {
      console.log(`✓ Found image in description (direct URL): ${directImageMatch[1]}`);
      return directImageMatch[1];
    }
    
    // Look for lumacdn image URLs specifically
    const lumaImageMatch = description.match(/(https?:\/\/images\.lumacdn\.com\/[^\s\)]+)/);
    if (lumaImageMatch) {
      console.log(`✓ Found Luma image in description: ${lumaImageMatch[1]}`);
      return lumaImageMatch[1];
    }
    
    return undefined;
  }

  private async extractEventImage(eventUrl: string): Promise<string | undefined> {
    try {
      const response = await fetch(eventUrl);
      if (!response.ok) return undefined;
      
      const html = await response.text();
      
      // Extract og:image meta tag
      const ogImageMatch = html.match(/<meta\s+property=["']og:image["']\s+content=["']([^"']+)["']/i);
      if (ogImageMatch) {
        return ogImageMatch[1];
      }
      
      // Fallback: look for twitter:image
      const twitterImageMatch = html.match(/<meta\s+name=["']twitter:image["']\s+content=["']([^"']+)["']/i);
      if (twitterImageMatch) {
        return twitterImageMatch[1];
      }
      
      return undefined;
    } catch (error) {
      console.warn(`Failed to extract image from ${eventUrl}:`, error);
      return undefined;
    }
  }
  
  async fetchEvents(period: 'past' | 'future' = 'past'): Promise<LumaEvent[]> {
    const response = await fetch(
      `${this.baseUrl}/calendar/list-events?calendar_api_id=${this.LUMA_CALENDAR_ID}&period=${period}`,
      {
        headers: {
          'accept': 'application/json',
          'x-luma-api-key': this.LUMA_API_KEY
        }
      }
    );
    
    if (!response.ok) {
      throw new Error(`Failed to fetch Luma events: ${response.status} - ${await response.text()}`);
    }
    
    const data = await response.json();
    
    // Debug: Show description content for recent events to check for images
    if (data.entries && data.entries.length > 0 && period === 'past') {
      const recentEvents = data.entries.filter(entry => 
        entry.event.start_at.startsWith('2025')
      ).slice(0, 1);
      
      if (recentEvents.length > 0) {
        const event = recentEvents[0];
        console.log('\n=== RECENT EVENT DESCRIPTION ANALYSIS ===');
        console.log(`Event: ${event.event.name}`);
        console.log(`Description length: ${(event.event.description_md || '').length} chars`);
        console.log(`Has description images: ${/!\[.*?\]\(https?:\/\//.test(event.event.description_md || '') || /https?:\/\/images\.lumacdn\.com/.test(event.event.description_md || '')}`);
        console.log('=== END ANALYSIS ===\n');
      }
    }
    
    return data.entries || [];
  }

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
      .slice(0, 5); // Last 5 events
    
    // Sort future events by date ascending (soonest first)
    const sortedFuture = futureEvents
      .filter(e => new Date(e.event.start_at) > now)
      .sort((a, b) => new Date(a.event.start_at).getTime() - new Date(b.event.start_at).getTime())
      .slice(0, 5); // Next 5 events
    
    // Fetch event-specific images for all events
    console.log('Extracting event-specific images...');
    const allEvents = [...sortedPast, ...sortedFuture];
    
    
    // Known generic series cover that we want to avoid
    const genericSeriesCover = 'https://images.lumacdn.com/event-covers/2a/5856fd94-de13-4f1f-94d0-8e72da4e8710.png';
    
    await Promise.all(
      allEvents.map(async (event) => {
        // Strategy 1: Look for images in the description first
        let imageUrl = this.extractImageFromDescription(event);
        
        // Strategy 2: If no description image or it's the generic cover, try extracting from event page
        if (!imageUrl || imageUrl === genericSeriesCover) {
          const extractedImage = await this.extractEventImage(event.event.url);
          if (extractedImage && extractedImage !== genericSeriesCover) {
            imageUrl = extractedImage;
          }
        }
        
        // Strategy 3: If still no unique image, use API cover_url as last resort
        if (!imageUrl) {
          imageUrl = event.event.cover_url;
        }
        
        event.event_image_url = imageUrl;
        
        // Debug logging for the most recent event
        if (event === sortedPast[0]) {
          console.log('\n=== IMAGE SELECTION DEBUG ===');
          console.log(`Event: ${event.event.name}`);
          console.log(`Description image: ${this.extractImageFromDescription(event) || 'none'}`);
          console.log(`API cover_url: ${event.event.cover_url}`);
          console.log(`Final selected: ${event.event_image_url}`);
          console.log('=== END DEBUG ===\n');
        }
      })
    );
    
    return { past: sortedPast, future: sortedFuture };
  }
}

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
  
  // Format date properly without locale issues
  const formattedDate = `${startTime.getUTCMonth() + 1}/${startTime.getUTCDate()}/${startTime.getUTCFullYear()}, ${startTime.getUTCHours()}:${startTime.getUTCMinutes().toString().padStart(2, '0')} UTC`;
  
  // Use event-specific image if available, fallback to cover_url
  const imageUrl = event.event_image_url || event.event.cover_url || 'No image';
  
  return `### ${dateStr}-${timeStr} - ${event.event.name}

**Description**: ${event.event.description || 'No description'}
**Date**: ${formattedDate}
**URL**: ${event.event.url}
**Image URL**: ${imageUrl}
${event.event.zoom_meeting_url ? `**Zoom URL**: ${event.event.zoom_meeting_url}` : ''}

`;
}

function validateEnvironment() {
  const required = ['LUMA_API_KEY'];
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
    console.log('Usage: bun run luma.ts fetch-recent-and-upcoming');
    process.exit(0);
  }
  
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

export { LumaClient };