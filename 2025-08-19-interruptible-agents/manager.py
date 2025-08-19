from __future__ import annotations

import asyncio

from agents.planner_agent import WebSearchItem, WebSearchPlan, plan_searches
from agents.search_agent import summarize_search_term
from agents.writer_agent import ReportData, write_research_report


class ResearchManager:
    def __init__(self):
        pass

    async def run(self, query: str) -> None:
        self._print_section(f"Research: {query}")
        self._print_info("Planning searches...")
        search_plan = await self._plan_searches(query)
        self._print_planned_searches(search_plan)

        self._print_info(f"Running {len(search_plan.searches)} searches...")
        search_results = await self._perform_searches(search_plan)

        self._print_info("Writing report...")
        report = await self._write_report(query, search_results)

        self._print_section("Report Summary")
        print(report.short_summary)

        self._print_section("Report")
        print(report.markdown_report)

        self._print_section("Follow Up Questions")
        for idx, question in enumerate(report.follow_up_questions, start=1):
            print(f"{idx}. {question}")

    async def _plan_searches(self, query: str) -> WebSearchPlan:
        return await plan_searches(query)

    async def _perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        num_completed = 0
        total = len(search_plan.searches)
        tasks = [asyncio.create_task(self._search(item)) for item in search_plan.searches]
        results = []
        for task in asyncio.as_completed(tasks):
            item, result = await task
            if result is not None:
                results.append(result)
                self._print_success(f"{item.query}")
            else:
                self._print_error(f"{item.query}")
            num_completed += 1
            self._print_progress(num_completed, total)
        return results

    async def _search(self, item: WebSearchItem) -> tuple[WebSearchItem, str | None]:
        try:
            summary = await summarize_search_term(term=item.query, reason=item.reason)
            return item, summary
        except Exception:
            return item, None

    async def _write_report(self, query: str, search_results: list[str]) -> ReportData:
        return await write_research_report(query=query, summaries=search_results)

    # ---------- Pretty printing helpers ----------
    def _print_section(self, title: str) -> None:
        line = "=" * max(12, len(title) + 4)
        print(f"\n{line}\n  {title}\n{line}")

    def _print_info(self, message: str) -> None:
        print(f"[ ] {message}")

    def _print_success(self, message: str) -> None:
        check = "\x1b[32m✓\x1b[0m"
        print(f"{check} {message}")

    def _print_error(self, message: str) -> None:
        cross = "\x1b[31m✗\x1b[0m"
        print(f"{cross} {message}")

    def _print_progress(self, completed: int, total: int) -> None:
        print(f"    progress: {completed}/{total}")

    def _print_planned_searches(self, plan: WebSearchPlan) -> None:
        self._print_section(f"Planned Searches ({len(plan.searches)})")
        for idx, item in enumerate(plan.searches, start=1):
            print(f"{idx}. {item.query} — {item.reason}")