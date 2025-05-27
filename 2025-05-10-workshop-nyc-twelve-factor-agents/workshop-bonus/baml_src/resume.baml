// Defining a data model.
class Resume {
  name string
  email string
  experience Experience[]
  skills string[]
}

class Experience {
  company Company @description(#"
    the legal company name
  "#)
  title string
  start_date string?
  end_date string?
  description string?
}

class Company {
  name string
  company_type "well-known" | "unknown"
  legal_name string? @description(#"
    best guess if the company is well-known
  "#) @alias(parent_company_legal_name)
}

enum CompanyType {
  WellKnown
  Subsidiary
  Unknown
}


// Create a function to extract the resume from a string.
function ExtractResume(resume: string?) -> Resume {
  // Specify a client as provider/model-name
  // you can use custom LLM params with a custom client name from clients.baml like "client CustomHaiku"
  client "openai/gpt-4o"
  prompt ###"
    Extract from this content:
    {{ resume }}

    {{ ctx.output_format }}

    dont use quotes around strings

    first list out companies to make sure you don't miss any
    - ..
    - ..
    ..

    { .. }
  "###
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
      - CV Engineer at XBOX

      Skills:
      - Rust
      - C++
    "#
  }
}


class Code {
  code string @description(#"
    use triple backticks to format multiline strings
    without quotes
    example:
    code: ```python
    ...
    ```
  "#)
  explanation string
}

function GenerateCode(prompt: string) -> Code {
  client "openai/gpt-4o"
  prompt #"
    Generate code for the following prompt:
    {{ prompt }}

    in python.

    {{ ctx.output_format(prefix="Answer like this:\n") }}
  "#
}

test generate_code {
  functions [GenerateCode]
  args {
    prompt #"
      Generate a function to calculate the factorial of a number.
    "#
  }
}
