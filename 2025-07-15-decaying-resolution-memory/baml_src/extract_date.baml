class Dates {
  dates string[]? @description(#"
    the dates related to the message in the format YYYY-MM-DD
  "#)
}

class NotFound {
  found false
}

// Create a function to redact PII from a string.
function ExtractDate(text: string) -> Dates | NotFound {
  client "anthropic/claude-opus-4-20250514" 
  // client "openai/claude-4" 
  prompt #"
    Extract the date from the following text in YYYY-MM-DD format.

    This is a long thread of messages, do you best to
    extract every detected date


    {{ _.role("user")}}
    {{ text }}

    {{ ctx.output_format }}
  "#
}


// Test the function with a sample resume. Open the VSCode playground to run this.
test extract_date {
  functions [ExtractDate]
  args {
    text #"
      Vaibhav Gupta
      vbv@boundaryml.com

      - engineer worked on vision models
      - worked on vision models at Google
      - worked on vision models at Microsoft

      - 2025-07-15
      - 2025-07-16
      - 2025-07-17
    "#
  }
}