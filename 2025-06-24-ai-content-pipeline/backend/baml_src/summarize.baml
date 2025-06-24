// Video summarization functions

class VideoSummary {
  main_takeaways string[] @description(#"
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
  bullet_points (string @stream.done)[]
}

// Summarize video transcript into key points
function SummarizeVideo(transcript: string, title: string?) -> VideoSummary {
  client "openai/gpt-4o"
  prompt #"
    Analyze this video transcript and create a comprehensive summary.
    {{ ctx.output_format }}

    This is from a video series called: "AI that works.". The audience is already familiar with LLMs
    and is more interested in the practical applications of LLMs and edge cases and nuances beyond surface level.

    Before answering, outline a very dense summary of the video.
    ```
    ...
    < very dense summary of the video >
    ...
    ```

    { ... }

    {{ _.role('user') }}
    {% if title %}Video Title: {{ title }}{% endif %}
    
    Transcript:
    {{ transcript }}
  "#
}