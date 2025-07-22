// Defining a data model.
class Txn {
  name string
  amount float
}

// Create a function to extract the resume from a string.
function ExtractTransactions(content: pdf) -> Txn[] {
  // Specify a client as provider/model-name
  // you can use custom LLM params with a custom client name from clients.baml like "client CustomHaiku"
  client "openai/gpt-4o" // Set OPENAI_API_KEY to use this client.
  prompt #"
    Extract all transactions from this content
    {{ ctx.output_format }}

    {{ _.role('user') }}
    {{ content }}
  "#
}



// Test the function with a sample resume. Open the VSCode playground to run this.
test chase {
  functions [ExtractTransactions]
  args {
    content {
      file "../example.pdf"
    }
  }
}
