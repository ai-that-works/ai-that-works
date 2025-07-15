// Create a function to redact PII from a string.
function RedactPII(text: string) -> string {
  // client "anthropic/claude-opus-4-20250514" 
  client "openai/gpt-4o-mini" 
  prompt #"
    Redact PII from this content, returning the full content with PII redacted.

    - first and last names
    - email addresses
    - company names



    {{ _.role("user")}}
    {{ text }}

    {{ ctx.output_format }}
  "#
}



// Test the function with a sample resume. Open the VSCode playground to run this.
test vaibhav_resume {
  functions [RedactPII]
  args {
    text #"
      Vaibhav Gupta
      vbv@boundaryml.com

      - engineer worked on vision models
      - worked on vision models at Google
      - worked on vision models at Microsoft

      also loves to eat pizza and play tennis
    "#
  }
}
