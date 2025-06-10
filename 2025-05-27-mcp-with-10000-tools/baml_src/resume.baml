class Actions {
  @@dynamic
}

class HumanMessage {
  message_type "request_clarification" | "respond_to_user"
  message string
}


class OrderedTools {
  tool_name string
  dependencies string[]
}

function PickAction(state: string) -> Actions | HumanMessage {
  client "openai/gpt-4o"
  prompt #"
    You are an agent with access to any number of tools.

    {{ ctx.output_format }}

    Help the user by picking an action for the following.

    {{ _.role('user') }}
    {{ state }}
  "#
}

test TestName {
  functions [PickAction]
  type_builder {
    class AddTool {
      intent "add_tool"
      a int
      b int
    }

    class SubtractTool {
      intent "subtract_tool"
      a int
      b int
    }

    dynamic class Actions {
      tools AddTool | SubtractTool
    }
  }
  args {
    state #"
      hello world
    "#
  }
}


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
