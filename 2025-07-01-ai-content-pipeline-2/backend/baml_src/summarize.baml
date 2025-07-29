// Video summarization functions

class VideoSummary {
  // timed_data TimeData[] @description(#"
  //   usually 5-10 minute semantic chunks (but exact timings from transcript)
  // "#)
  main_takeaways (string)[] @description(#"
    use triple quotes for multi-line strings (this can be dense)
    [
    """
    string content
    """,
    """
    string content
    """,
    ...
    ]
  "#)
  key_topics string[]
  bullet_points (string)[] @alias(takeaways) @description(#"
    action items listeners can do to improve their skills
  "#)
}

class TimeData {
  start_time string
  end_time string
  summary string
}

// Summarize video transcript into key points
function SummarizeVideo(transcript: string, title: string?) -> VideoSummary {
  client OpenaiFallback
  prompt #"
    {{ _.role('user') }}
    {% if title %}Video Title: {{ title }}{% endif %}
    
    Transcript:
    {{ transcript }}

    {{ _.role('user') }}
    Analyze this video transcript and create a comprehensive summary.
    {{ ctx.output_format }}

    This is from a video series called: "AI that works.". The audience is already familiar with LLMs
    and is more interested in the practical applications of LLMs and edge cases and nuances beyond surface level.

    Before answering, outline a very dense summary of the video.

    Since the vidoes are pretty long, try and have time ranges (synced to the transcript)

    ...topic 2 para...
    ...
    </ very dense summary of the video >
    
    { .. } // schema 

    {{ _.role('user') }}
    {% if title %}Video Title: {{ title }}{% endif %}
    
    Transcript:
    {{ transcript }}
  "#
}
