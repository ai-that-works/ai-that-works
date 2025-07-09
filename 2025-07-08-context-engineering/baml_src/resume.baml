// Defining a data model.
class Resume {
  action "extract_complete_resume"
  name string
  email string
  experience Experience[]
  skills string[]
}

class Experience {
  company string
  company_type "startup" | "enterprise"
  title string
  start_date string
  end_date string
  description string
}

class RequestMoreInformation {
  action "request_more_information"
  requests string[]
  reason string
}

// Create a function to extract the resume from a string.
function ExtractResume(resume: string) -> Resume | RequestMoreInformation {
  // Specify a client as provider/model-name
  // you can use custom LLM params with a custom client name from clients.baml like "client CustomHaiku"
  client "google-ai/gemini-2.0-flash-001" // Set OPENAI_API_KEY to use this client.
  prompt #"
    Extract from this content:
    {{ ctx.output_format }}

    If information is missing, request more information before continuing.

    {{ _.role('user') }}
    {{ resume }}
  "#
}



// Test the function with a sample resume. Open the VSCode playground to run this.
test vaibhav_resume {
  functions [ExtractResume]
  args {
    resume #"
      Vaibhav Gupta
      vbv@boundaryml.com

      Experience:
      - Founder at BoundaryML
      - CV Engineer at Google
      - CV Engineer at Microsoft

      Skills:
      - Rust
      - C++
    "#
  }
}
