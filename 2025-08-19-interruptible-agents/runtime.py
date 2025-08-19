from __future__ import annotations

import asyncio
import threading
import time
from collections import deque
from dataclasses import dataclass
from queue import Queue, Empty
from typing import Deque, Optional

from manager import ResearchManager


@dataclass
class ProgressEvent:
    timestamp: float
    event_type: str
    message: str


@dataclass
class Message:
    kind: str  # "info" | "replan" | "cancel"
    text: str = ""


class ConversationRuntime:
    def __init__(self, convo_id: str, max_events: int = 500) -> None:
        self.convo_id = convo_id
        self.message_queue: Queue[Message] = Queue()
        self.events: Deque[ProgressEvent] = deque(maxlen=max_events)
        self.events_cv = threading.Condition()
        self.lock = threading.RLock()
        self.cancel_event = threading.Event()
        self.new_msg_event = threading.Event()
        self.phase_index: int = 0
        self.status: str = "idle"

    def emit(self, event_type: str, message: str) -> None:
        with self.events_cv:
            self.events.append(ProgressEvent(time.monotonic(), event_type, message))
            self.events_cv.notify_all()

    def queue_message(self, msg: Message) -> None:
        if msg.kind == "cancel":
            self.cancel_event.set()
        else:
            self.message_queue.put(msg)
            self.new_msg_event.set()


class RuntimeAwareResearchManager(ResearchManager):
    def __init__(self, runtime: ConversationRuntime) -> None:
        super().__init__()
        self.runtime = runtime

    # Override printing helpers to route to event stream
    def _print_section(self, title: str) -> None:  # type: ignore[override]
        self.runtime.emit("section", title)

    def _print_info(self, message: str) -> None:  # type: ignore[override]
        self.runtime.emit("info", message)

    def _print_success(self, message: str) -> None:  # type: ignore[override]
        self.runtime.emit("success", message)

    def _print_error(self, message: str) -> None:  # type: ignore[override]
        self.runtime.emit("error", message)

    def _print_progress(self, completed: int, total: int) -> None:  # type: ignore[override]
        self.runtime.emit("progress", f"{completed}/{total}")


class AgentThread(threading.Thread):
    def __init__(self, runtime: ConversationRuntime, initial_query: str) -> None:
        super().__init__(daemon=True)
        self.runtime = runtime
        self.initial_query = initial_query
        self.current_query = initial_query
        self._stopped = threading.Event()

    def stop(self) -> None:
        self._stopped.set()

    def run(self) -> None:  # noqa: C901 - keep simple even if a bit long
        mgr = RuntimeAwareResearchManager(self.runtime)

        # Dedicated asyncio loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            self.runtime.status = "running"
            self.runtime.emit("start", f"Research: {self.initial_query}")

            # Phase 1: Planning
            if self._boundary_check():
                self._finish("cancelled")
                return
            self.runtime.phase_index = 1
            self.runtime.emit("phase", "Planning searches...")
            search_plan = loop.run_until_complete(mgr._plan_searches(self.current_query))
            # Provide a structured echo similar to original manager
            self.runtime.emit("section", f"Planned Searches ({len(search_plan.searches)})")
            for item in search_plan.searches:
                self.runtime.emit("plan_item", f"{item.query} — {item.reason}")

            # Phase 2: Searches
            if self._boundary_check():
                self._finish("cancelled")
                return
            self.runtime.phase_index = 2
            self.runtime.emit("phase", f"Running {len(search_plan.searches)} searches...")
            search_results = loop.run_until_complete(mgr._perform_searches(search_plan))

            # Phase 3: Write report
            if self._boundary_check():
                self._finish("cancelled")
                return
            self.runtime.phase_index = 3
            self.runtime.emit("phase", "Writing report...")
            report = loop.run_until_complete(mgr._write_report(self.current_query, search_results))

            # Output
            self.runtime.emit("section", "Report Summary")
            self.runtime.emit("report_summary", report.short_summary)
            self.runtime.emit("section", "Report")
            self.runtime.emit("report_markdown", report.markdown_report)
            self.runtime.emit("section", "Follow Up Questions")
            for idx, q in enumerate(report.follow_up_questions, start=1):
                self.runtime.emit("follow_up", f"{idx}. {q}")

            self._finish("done")
        finally:
            try:
                loop.run_until_complete(loop.shutdown_asyncgens())
            finally:
                loop.close()

    def _boundary_check(self) -> bool:
        """Return True if should stop (cancelled). Drain and apply messages otherwise."""
        if self.runtime.cancel_event.is_set() or self._stopped.is_set():
            return True

        # Drain queue non-blocking and coalesce info/replan
        new_instructions: list[str] = []
        saw_replan = False
        while True:
            try:
                msg = self.runtime.message_queue.get_nowait()
            except Empty:
                break
            if msg.kind == "cancel":
                self.runtime.cancel_event.set()
            elif msg.kind == "replan":
                saw_replan = True
                if msg.text:
                    new_instructions.append(msg.text)
            else:  # info
                if msg.text:
                    new_instructions.append(msg.text)

        if self.runtime.cancel_event.is_set():
            return True

        if new_instructions:
            # Merge instructions by appending to the working query
            merged = "\n".join(new_instructions)
            if saw_replan:
                # Replace the query semantics on replan
                self.current_query = merged
                self.runtime.emit("replan", f"Replanned with new query:")
                self.runtime.emit("replan_query", self.current_query)
            else:
                # Augment current query context
                self.current_query = f"{self.current_query}\n\nAdditional instructions:\n{merged}"
                self.runtime.emit("info_merge", "Merged additional instructions into context")

        # Clear the "new message" edge trigger if no more pending
        if self.runtime.message_queue.empty():
            self.runtime.new_msg_event.clear()

        return False

    def _finish(self, status: str) -> None:
        self.runtime.status = status
        self.runtime.emit("done", status)


# Registry helpers for single-process usage
class InMemoryAgentSystem:
    def __init__(self) -> None:
        self._convos: dict[str, ConversationRuntime] = {}
        self._threads: dict[str, AgentThread] = {}
        self._lock = threading.RLock()

    def start(self, convo_id: str, query: str) -> ConversationRuntime:
        with self._lock:
            if convo_id in self._threads and self._threads[convo_id].is_alive():
                raise RuntimeError(f"Conversation '{convo_id}' already running")
            runtime = ConversationRuntime(convo_id)
            thread = AgentThread(runtime, query)
            self._convos[convo_id] = runtime
            self._threads[convo_id] = thread
            thread.start()
            return runtime

    def queue(self, convo_id: str, msg: Message) -> None:
        runtime = self._require_runtime(convo_id)
        runtime.queue_message(msg)

    def cancel(self, convo_id: str) -> None:
        runtime = self._require_runtime(convo_id)
        runtime.queue_message(Message(kind="cancel"))

    def get_runtime(self, convo_id: str) -> ConversationRuntime:
        return self._require_runtime(convo_id)

    def is_done(self, convo_id: str) -> bool:
        rt = self._require_runtime(convo_id)
        return rt.status in {"done", "cancelled"}

    def _require_runtime(self, convo_id: str) -> ConversationRuntime:
        with self._lock:
            if convo_id not in self._convos:
                raise KeyError(f"Unknown conversation '{convo_id}'")
            return self._convos[convo_id]


