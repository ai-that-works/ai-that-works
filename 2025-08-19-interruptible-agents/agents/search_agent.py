from baml_client import b


async def summarize_search_term(term: str, reason: str) -> str:
    """Summarize expected findings for a web search term using BAML.

    This calls the BAML function `SummarizeSearchTerm` defined in `baml_src/research.baml`.
    If you have actual snippets from a web search, consider inlining them into the term or
    extending the BAML function signature to pass them explicitly.
    """
    return await b.SummarizeSearchTerm(term=term, reason=reason)


__all__ = [
    "summarize_search_term",
]
