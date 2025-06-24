// Video content generation models
class VideoSummary {
  bullet_points string[]
  key_topics string[]
  main_takeaways string[]
}

class EmailDraft {
  subject string
  body string
  call_to_action string
}

class TwitterThread {
  tweets string[]
  hashtags string[]
}

class LinkedInPost {
  content string
  hashtags string[]
}

// Summarize video transcript into key points
function SummarizeVideo(transcript: string, title: string?) -> VideoSummary {
  client CustomGPT4oMini
  prompt #"
    Analyze this video transcript and create a comprehensive summary.
    
    {% if title %}Video Title: {{ title }}{% endif %}
    
    Transcript:
    {{ transcript }}
    
    Extract:
    1. Key bullet points that capture the main content
    2. Important topics discussed
    3. Main takeaways and insights
    
    {{ ctx.output_format }}
  "#
}

// Generate professional email draft
function GenerateEmailDraft(summary: VideoSummary, video_title: string?) -> EmailDraft {
  client CustomGPT4oMini
  prompt #"
    Create a professional email announcing this video content.
    
    {% if video_title %}Video Title: {{ video_title }}{% endif %}
    
    Video Summary:
    Bullet Points: {{ summary.bullet_points }}
    Key Topics: {{ summary.key_topics }}
    Main Takeaways: {{ summary.main_takeaways }}
    
    Write a compelling email that:
    - Has an engaging subject line
    - Summarizes the video value proposition 
    - Includes a clear call-to-action
    - Maintains a professional but approachable tone
    
    {{ ctx.output_format }}
  "#
}

// Generate Twitter thread
function GenerateTwitterThread(summary: VideoSummary, video_title: string?) -> TwitterThread {
  client CustomGPT4oMini
  prompt #"
    Create an engaging Twitter thread about this video content.
    
    {% if video_title %}Video Title: {{ video_title }}{% endif %}
    
    Video Summary:
    Bullet Points: {{ summary.bullet_points }}
    Key Topics: {{ summary.key_topics }}
    Main Takeaways: {{ summary.main_takeaways }}
    
    Create a thread that:
    - Starts with a hook tweet
    - Breaks down key insights across 3-5 tweets
    - Uses relevant hashtags
    - Encourages engagement
    - Each tweet should be under 280 characters
    
    {{ ctx.output_format }}
  "#
}

// Generate LinkedIn post
function GenerateLinkedInPost(summary: VideoSummary, video_title: string?) -> LinkedInPost {
  client CustomGPT4oMini
  prompt #"
    Create a professional LinkedIn post about this video content.
    
    {% if video_title %}Video Title: {{ video_title }}{% endif %}
    
    Video Summary:
    Bullet Points: {{ summary.bullet_points }}
    Key Topics: {{ summary.key_topics }}
    Main Takeaways: {{ summary.main_takeaways }}
    
    Write a LinkedIn post that:
    - Starts with an engaging hook
    - Highlights key professional insights
    - Uses appropriate hashtags
    - Encourages professional discussion
    - Maintains thought leadership tone
    
    {{ ctx.output_format }}
  "#
}