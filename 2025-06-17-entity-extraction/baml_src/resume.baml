// Defining a data model.
class Resume {
  name string
  email string
  experience Experience[]
  skills string[]
}

class Experience {
  company Company @description(#"
    The legal company name
  "#)
  title string
}

class Company {
  name string @description(#"
    verbatim from content
  "#)
  company_type "well_known" | "well_known_subsidary" | "startup" 
  legal_name string? @description(#"
    if "well_known", best guess of the legal name of the company 
    if "well_known_subsidary", best guess of the legal name of the owning company
    skip if startup
  "#)
}

// Create a function to extract the resume from a string.
function ExtractResume(resume: string) -> Resume {
  // Specify a client as provider/model-name
  // you can use custom LLM params with a custom client name from clients.baml like "client CustomHaiku"
  client "ollama/phi4:latest" // Set OPENAI_API_KEY to use this client.
  prompt #"
    Extract from this content:
    {{ resume }}

    {{ ctx.output_format }}
  "#
}

class CompanyClue {
  clues string[]
  good_google_searches Search[]
}

class Search {
  search string
  priority "high" | "medium" | "low" @description(#"
    based on which queries i should run first
  "#)
}

function ExtractCompanyClues(resume: string, target_company: string) -> CompanyClue {
  client "ollama/phi4:latest"
  prompt #"
    Given this resume, tell me all the clues that may help me find information about the company {{ target_company }}.

    specifically i want to find the legal name of the company

    {{ ctx.output_format }}

    Resume:
    {{ resume }}
  "#
}

function ExtractLegalName(content: string, target_company: string) -> string {
  client "ollama/phi4:latest"
  prompt #"
    Given this content, tell me the legal name of the company {{ target_company }}.
    {{ ctx.output_format }}
    Content:
    {{ content }}
  "#
}

test vaibhav_resume {
  functions [ExtractCompanyClues]
  args {
    target_company "BoundaryML"
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


test vaibhav_resume_ambiguous {
  functions [ExtractResume]
  args {
    resume #"
      Vaibhav Gupta
      vbv@boundaryml.com

      Experience:
      - Founder at BoundaryML
      - CV Engineer at GCP
      - CV Engineer at XBOX

      Skills:
      - Rust
      - C++
    "#
  }
}
