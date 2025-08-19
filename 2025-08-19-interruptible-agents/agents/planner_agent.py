from baml_client import b
from baml_client.types import WebSearchItem, WebSearchPlan


async def plan_searches(query: str) -> WebSearchPlan:
    """Plan a set of web searches for a given research query using BAML.

    This calls the BAML function `PlanWebSearches` defined in `baml_src/research.baml`.
    """
    return await b.PlanWebSearches(query)


__all__ = [
    "WebSearchItem",
    "WebSearchPlan",
    "plan_searches",
]
