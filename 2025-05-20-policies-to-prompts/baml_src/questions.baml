// Defining a data model.
class Question {
  question string @description("A binary question that can be answered to determine whether the rule was followed")
  citation_str string @description("The exact text from the document that inspired the question")
  citation string? @description("The section and header from the document that inspired the question")
}

// Create a function to extract the resume from a string.
function ExtractQuestions(document: string) -> Question[] {
  // Specify a client as provider/model-name
  // you can use custom LLM params with a custom client name from clients.baml like "client CustomHaiku"
  client "openai/gpt-4o" // Set OPENAI_API_KEY to use this client.
  prompt #"

    You are a compliance expert. You read
    policy documents and create questions
    for an auditor to answer. The questions
    should be binary questions that can be
    answered to determine whether the rule
    was followed.

    The document will have many rules, output
    questions for all of them.

    {{ _.role("user") }}

    Here is the document you are auditing:

    {{ document }}

    {{ ctx.output_format }}
  "#
}



// Test the function with a sample resume. Open the VSCode playground to run this.
test sarbanes_oxley {
  functions [ExtractQuestions]
  args {
    document #"

      Section 101.100

      Members must not accept gifts or favors from any person or entity that is a subject of the Company's business, including suppliers, customers, competitors, or other third parties.

    "#
  }
  @@assert(output, {{"gifts" in output[0].citation_str}})
}
