// Research workflow agents implemented the "BAML way" as functions and types.

// Planner output types
class WebSearchItem {
  reason string @description("Your reasoning for why this search is important to the query.")
  query string  @description("The search term to use for the web search.")
}

class WebSearchPlan {
  searches WebSearchItem[] @description("A list of web searches to perform to best answer the query.")
}

// Writer output type
class ReportData {
  short_summary string         @description("A short 2-3 sentence summary of the findings.")
  markdown_report string       @description("The final report in markdown format.")
  follow_up_questions string[] @description("Suggested topics to research further.")
}

// Planner: plan web searches for a query
function PlanWebSearches(query: string) -> WebSearchPlan {
  client CustomGPT4o
  prompt #"
    You are a helpful research assistant. Given a query, come up with a set of web searches
    to perform to best answer the query. Output between 5 and 20 terms to query for.

    {{ ctx.output_format }}

    {{ _.role('user') }}
    Query: {{ query }}
  "#
}

test TestName {
  functions [PlanWebSearches]
  args {
    query #"
      Why is a woodpeckers tongue so long?
    "#
  }
}


client<llm> WithWebSearch {
  provider openai-responses
  options {
    model "gpt-4o"
    tools [{type "web_search_preview"}]
    tool_choice "required"
  }
}

// Search: summarize results for a given term
// Note: This function does not perform the web search. It should be called with
// any gathered snippets or context as part of the inputs if available.
function SummarizeSearchTerm(term: string, reason: string) -> string {
  client WithWebSearch
  prompt #"
    You are a research assistant. Given a search term and the reason for searching,
    produce a concise summary of likely findings. If you are provided with snippets
    or context, incorporate them. The summary must be 2-3 paragraphs and less than
    300 words. Capture the main points. Write succinctly; grammar can be informal.
    Do not include any additional commentary other than the summary itself.

    {{ _.role('system') }}
    Keep the response under 300 words in 2-3 paragraphs.

    {{ _.role('user') }}
    Search term: {{ term }}
    Reason: {{ reason }}
  "#
}

test TestName {
  functions [SummarizeSearchTerm]
  args {
    term #"
      dogs
    "#
    reason #"
      the user is allergic to dogs
    "#
  }
}


// Writer: generate a detailed report from the query and search summaries
function WriteResearchReport(query: string, summaries: string[]) -> ReportData {
  client CustomGPT4o
  prompt #"
    You are a senior researcher tasked with writing a cohesive report for a research query.
    You will be provided with the original query, and some initial research done by a research assistant.

    You should first come up with an outline for the report that describes the structure and flow of the report.
    Then, generate the report and return that as your final output.

    The final output should be in markdown format, and it should be lengthy and detailed.
    Aim for 5-10 pages of content, at least 1000 words.

    {{ ctx.output_format }}

    {{ _.role('user') }}
    Original query: {{ query }}
    Summarized search results: 
    {% for summary in summaries %}
    {{ loop.index }}. {{ summary }}
    -
    {% endfor %}
  "#
}



test TestName {
  functions [WriteResearchReport]
  args {
    query #"
      Why is a woodpeckers tongue so long?
    "#
    summaries [
      #"
        Woodpeckers have a long tongue to help them peck at trees and get insects.
      "#,
      #"
        The biology of woodpeckers is fascinating.
      "#
    ]
  }
}
