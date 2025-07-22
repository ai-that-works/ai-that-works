// Defining a data model.
class Txn {
  name string
  amount float
}

class Answer {
  page_type "transactions" | "cover_page" | "terms_and_conditions" | "non-financial"
  number_of_transactions int
  reason string
}

function HasTransactions(page: image) -> Answer {
  client CustomHaiku
  prompt #"
    Does this page have specific financial transactions (credit / debit)?
    {{ ctx.output_format }}

    {{ _.role('user') }}
    {{ page }}
  "#
}

test title_page {
  functions [HasTransactions]
  args {
    page {
      file "../data/page_0.png"
    }
  }
}

test page_1 {
  functions [HasTransactions]
  args {
    page {
      file "../data/page_1.png"
    }
  }
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
