// Content generation functions for different platforms

template_string EmailExample() #"
    Hello First Name,

    This weeks 🦄 ai that works session was on "Entity Resolution: Extraction, Deduping, and Enriching"! 

    The full recording, code, and diagrams from the session are now available on GitHub:
    https://github.com/hellovai/ai-that-works

    We covered a lot on building robust entity resolution pipelines. Here’s a super quick recap:

    It's a Multi-Stage System, Not Just One Prompt: Effective entity resolution involves an initial LLM pass for extraction, crucial validation against your existing database of known entities (because you can't just stuff your whole DB into the prompt!), and then targeted enrichment for anything new or unconfirmed.
    Your Entity Database is a Living Asset: The real power comes from continuously growing and refining your canonical entity list. For new entities (like "BoundaryML" from our example), kick off an asynchronous enrichment pipeline – think LLM-powered research and web search – with a review process to keep your master list accurate and evolving.

    If you remember one thing from this session:
    Entity Resolution is an engineered system. It’s an initial LLM pass for extraction, robust validation logic against your known entities, and a separate, resilient pipeline to research, verify, and add new entities to your database over time.

    We also had a fascinating session last week about "Cracking the Prompting Interview" for algorithms to make prompts better, video/whiteboards/code are on the Github!

    Our next session on [June 24th] will be all about "Building an AI Content Pipeline" – exploring how to use an AI pipeline to write emails like this from zoom recordings and transcripts.
    Sign up here: https://lu.ma/zcf5c8yd
    If you have any questions, reply to this email or ask on Discord: https://www.boundaryml.com/discord. We read every message! Happy coding 🧑‍💻

    Vaibhav & Dex
"#

// Generate professional email draft
function GenerateEmailDraft(summary: VideoSummary, transcript: string?, video_title: string?) -> EmailDraft {
  client CustomGPT4oMini
  prompt #"
    Create a professional email announcing this video content on behalf of Vaibhav and Dex.

    {{ ctx.output_format }}

    An example great email for a prior video was this:
    {{ EmailExample() }}

    {{ _.role('user') }}
    {% if video_title %}Video Title: {{ video_title }}{% endif %}

    {% if transcript %}
    Full Transcript:
    {{ transcript }}
    {% endif %}

    Video Summary:
    {% for point in summary.bullet_points %}
    - {{ point }}
    {% endfor %}

    Key Topics: 
    {% for topic in summary.key_topics %}
    - {{ topic }}
    {% endfor %}

    Main Takeaways:
    {% for takeaway in summary.main_takeaways %}
    - {{ takeaway }}
    {% endfor %}
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

// Refine email draft based on user feedback
function RefineEmailDraft(
  current_draft: EmailDraft,
  feedback: string,
  summary: VideoSummary,
  transcript: string?,
  video_title: string?
) -> EmailDraft {
  client "openai/gpt-4o"
  prompt #"
    You are helping refine an email draft based on user feedback. Use the video content as context to make informed improvements.

    {{ ctx.output_format }}

    {% if video_title %}Video Title: {{ video_title }}{% endif %}

    Current Email Draft:
    Subject: {{ current_draft.subject }}
    Body: {{ current_draft.body }}
    Call to Action: {{ current_draft.call_to_action }}

    User Feedback: {{ feedback }}

    Video Summary Context:
    Key Points: {{ summary.bullet_points }}
    Topics: {{ summary.key_topics }}
    Takeaways: {{ summary.main_takeaways }}

    {% if transcript %}
    Original Transcript (for reference):
    {{ transcript }}
    {% endif %}

    Instructions:
    1. Carefully analyze the user's feedback to understand what they want changed
    2. Use the video summary and transcript to ensure accuracy and relevance
    3. Maintain the professional email tone while implementing the requested changes
    4. Keep the email structure (subject, body, call-to-action) but improve based on feedback
    5. If feedback is vague, make reasonable improvements that enhance clarity and engagement

    Return an improved email that addresses the user's feedback while staying true to the video content.
  "#
}

// Refine Twitter thread based on user feedback
function RefineTwitterThread(
  current_draft: TwitterThread,
  feedback: string,
  summary: VideoSummary,
  transcript: string?,
  video_title: string?
) -> TwitterThread {
  client "openai/gpt-4o"
  prompt #"
    You are helping refine a Twitter thread based on user feedback. Use the video content as context to make informed improvements.

    {{ ctx.output_format }}

    {% if video_title %}Video Title: {{ video_title }}{% endif %}

    Current Twitter Thread:
    Tweets: {{ current_draft.tweets }}
    Hashtags: {{ current_draft.hashtags }}

    User Feedback: {{ feedback }}

    Video Summary Context:
    Key Points: {{ summary.bullet_points }}
    Topics: {{ summary.key_topics }}
    Takeaways: {{ summary.main_takeaways }}

    {% if transcript %}
    Original Transcript (for reference):
    {{ transcript }}
    {% endif %}

    Instructions:
    1. Carefully analyze the user's feedback to understand what they want changed
    2. Use the video summary and transcript to ensure accuracy and relevance
    3. Maintain Twitter best practices (280 char limit, engaging hooks, clear structure)
    4. Keep the thread format but improve content based on feedback
    5. Update hashtags if needed to better reflect the refined content
    6. Ensure tweets flow well together and tell a cohesive story

    Return an improved Twitter thread that addresses the user's feedback while staying true to the video content.
  "#
}

// Refine LinkedIn post based on user feedback
function RefineLinkedInPost(
  current_draft: LinkedInPost,
  feedback: string,
  summary: VideoSummary,
  transcript: string?,
  video_title: string?
) -> LinkedInPost {
  client "openai/gpt-4o"
  prompt #"
    You are helping refine a LinkedIn post based on user feedback. Use the video content as context to make informed improvements.

    {{ ctx.output_format }}

    {% if video_title %}Video Title: {{ video_title }}{% endif %}

    Current LinkedIn Post:
    Content: {{ current_draft.content }}
    Hashtags: {{ current_draft.hashtags }}

    User Feedback: {{ feedback }}

    Video Summary Context:
    Key Points: {{ summary.bullet_points }}
    Topics: {{ summary.key_topics }}
    Takeaways: {{ summary.main_takeaways }}

    {% if transcript %}
    Original Transcript (for reference):
    {{ transcript }}
    {% endif %}

    Instructions:
    1. Carefully analyze the user's feedback to understand what they want changed
    2. Use the video summary and transcript to ensure accuracy and relevance
    3. Maintain professional LinkedIn tone and thought leadership voice
    4. Improve content structure, clarity, and engagement based on feedback
    5. Update hashtags if needed to better reflect the refined content
    6. Ensure the post encourages professional discussion and adds value

    Return an improved LinkedIn post that addresses the user's feedback while staying true to the video content.
  "#
}

// Generate YouTube video title
function GenerateYouTubeTitle(
  summary: VideoSummary,
  transcript: string?,
  current_title: string?
) -> string {
  client "openai/gpt-4o"
  prompt #"
    Create an engaging YouTube video title that will maximize views and accurately represent the content.

    {% if current_title %}Current Title: {{ current_title }}{% endif %}

    Video Summary:
    Key Points: {{ summary.bullet_points }}
    Topics: {{ summary.key_topics }}
    Takeaways: {{ summary.main_takeaways }}

    {% if transcript %}
    Transcript (for reference):
    {{ transcript }}
    {% endif %}

    Guidelines for YouTube titles:
    1. 60 characters or less (optimal for mobile display)
    2. Include compelling keywords that people search for
    3. Create curiosity or promise value
    4. Use power words: "Ultimate", "Secret", "Proven", "Essential", etc.
    5. Consider numbers and lists: "5 Ways", "Top 10", etc.
    6. Avoid clickbait - be accurate to content
    7. Front-load the most important keywords
    8. Consider your target audience (AI/tech professionals)

    This is for "AI that works" series - practical AI applications, not surface-level content.
    The audience is familiar with LLMs and wants actionable insights.

    Return ONLY the title text, nothing else.
  "#
}