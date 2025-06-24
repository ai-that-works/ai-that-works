// Video summarization functions

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