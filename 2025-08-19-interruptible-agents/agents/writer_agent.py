from baml_client import b
from baml_client.types import ReportData


async def write_research_report(query: str, summaries: list[str]) -> ReportData:
    """Write a detailed research report using BAML.

    This calls the BAML function `WriteResearchReport` defined in `baml_src/research.baml`.
    """
    return await b.WriteResearchReport(query=query, summaries=summaries)


__all__ = [
    "ReportData",
    "write_research_report",
]
