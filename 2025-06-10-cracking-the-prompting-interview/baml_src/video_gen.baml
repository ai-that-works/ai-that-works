class ScriptSegment {
  content string @description(#"
    use triple quote strings to format multiple lines of text
    {
      content: """
      ...
      """
    }
  "#)
  background_image string? @description(#"
    a description of a background image that is like a buisness insider video
  "#)
  duration int @alias("estimated_duration_seconds") transition "cut" | "fade" | "dissolve" @description("Type of transition to next segment") 
}

class SegmentationPlan {
  segments ScriptSegment[]
  totalSegments int
  averageSegmentDuration float
}

function AnalyzeScript(script: string, pacing: "fast" | "medium" | "slow") -> SegmentationPlan {
  client "openai/gpt-4o-mini"
  prompt #"
    Create a segmentation plan for the following script.
    Break it into logical segments considering the requested pacing.

    For each segment:
    - Ensure it contains a complete thought or idea
    - Estimate a reasonable duration in seconds
    - Suggest an appropriate transition type (cut, fade, dissolve, etc.)
    
    I want a {{ pacing }} pacing.
    {% if pacing == "fast" %}
    More frequent cuts (10-15 seconds per segment)

    150 words per minute is average speaking speed.
    {% elif pacing == "medium" %}
    Balanced pacing (15-30 seconds per segment)

    120 words per minute is average speaking speed.
    {% elif pacing == "slow" %}
    Fewer cuts (30-60 seconds per segment)

    100 words per minute is average speaking speed.
    {% endif %}

    {{ ctx.output_format }}

    {{ _.role("user") }} Script: {{ script }}
  "#
}

test FastPacingTest {
  functions [AnalyzeScript]
  args {
    script #"
      Welcome to our product showcase. This innovative device transforms how you work.
      It features an ergonomic design and smart connectivity. Let's explore its key features.
    "#
    pacing "fast"
  }
}

test SlowPacingTest {
  functions [AnalyzeScript]
  args {
    script #"
      Computing's journey began centuries before smartphones existed. Charles Babbage designed the first mechanical computer in the 1800s, while Ada Lovelace wrote what many consider the first computer program. Fast-forward to World War Two, when Alan Turing cracked the Enigma code and laid foundations for artificial intelligence. The 1940s brought us ENIAC, a room-sized beast that could barely match today's calculators. Then came the transistor revolution, shrinking computers from warehouses to desktops. Steve Jobs and Bill Gates turned computers into household items, while Tim Berners-Lee gave us the World Wide Web. Today, thanks to pioneers like Grace Hopper, who debugged the first computer "bug," we carry more computing power in our pockets than NASA used to reach the moon.
    "#
    pacing "slow"
  }
}
