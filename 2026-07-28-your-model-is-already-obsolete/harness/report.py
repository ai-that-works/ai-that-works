"""What a model scored on the corpus.

Deliberately flat and boring. `gate.py` is written live on stage, so
whatever it consumes has to be obvious at a glance — if the presenter has
to explain this file before writing the gate, the live segment dies.

Three dimensions, because those are the three the swap decision turns on:
accuracy, money, and speed.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field


@dataclass(frozen=True)
class CaseResult:
    """One corpus case, run once against one model."""

    case: str
    passed: bool
    failures: tuple[str, ...] = ()
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0
    output: str = ""


@dataclass(frozen=True)
class Report:
    """Everything the gate needs to judge one model."""

    model: str
    results: list[CaseResult] = field(default_factory=list)

    #: `None` means the price is NOT VERIFIED. It must stay `None` all the
    #: way to the gate — coercing it to 0.0 makes an unpriced model look
    #: free, sail through the cost check at 0.00x, and produce a
    #: confident PASS that is simply wrong.
    usd_per_1m_prompt: float | None = None
    usd_per_1m_completion: float | None = None

    @property
    def priced(self) -> bool:
        return self.usd_per_1m_prompt is not None and self.usd_per_1m_completion is not None

    @property
    def accuracy(self) -> float:
        """Fraction of cases passed, 0.0 - 1.0."""
        if not self.results:
            return 0.0
        return sum(r.passed for r in self.results) / len(self.results)

    @property
    def cost_per_call(self) -> float | None:
        """Mean USD per call. `None` when the price is unverified."""
        if not self.results or not self.priced:
            return None
        prompt = statistics.mean(r.prompt_tokens for r in self.results)
        completion = statistics.mean(r.completion_tokens for r in self.results)
        return (
            prompt * self.usd_per_1m_prompt + completion * self.usd_per_1m_completion
        ) / 1_000_000

    @property
    def p95_latency_ms(self) -> float:
        """95th percentile latency. p95 not mean: the tail is the UX."""
        if not self.results:
            return 0.0
        ordered = sorted(r.latency_ms for r in self.results)
        idx = min(int(len(ordered) * 0.95), len(ordered) - 1)
        return ordered[idx]

    @property
    def failed_cases(self) -> list[CaseResult]:
        """The cases to name out loud when the gate says no."""
        return [r for r in self.results if not r.passed]
