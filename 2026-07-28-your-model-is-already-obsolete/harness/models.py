"""The cast, and what each one costs.

Prices are USD per 1M tokens. `None` means NOT VERIFIED — the gate will
refuse to judge cost for that model rather than quietly using a made-up
number, because a fabricated price produces a confident wrong swap
decision, which is worse than no decision.

Verified 2026-07-27 against provider pricing pages. Re-check before the
recording; `claude-sonnet-5` in particular is on introductory pricing that
rises on 2026-09-01.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Model:
    #: BAML client name, as declared in baml_src/clients.baml
    client: str
    #: Provider's own model id, for the record
    model_id: str
    usd_per_1m_prompt: float | None
    usd_per_1m_completion: float | None
    note: str = ""

    @property
    def priced(self) -> bool:
        return self.usd_per_1m_prompt is not None and self.usd_per_1m_completion is not None


INCUMBENT = Model(
    client="IncumbentGPT4o",
    model_id="gpt-4o",
    usd_per_1m_prompt=2.50,
    usd_per_1m_completion=10.00,
    note=(
        "Obsolete, not deprecated. No announced OpenAI EOL as of 2026-07-27, "
        "but de-listed from the models index, comparison page and pricing "
        "page. Still live, still priced. Fastest model in this cast."
    ),
)

CANDIDATES = [
    Model(
        client="CandSonnet5",
        model_id="claude-sonnet-5",
        usd_per_1m_prompt=2.00,
        usd_per_1m_completion=10.00,
        note="Introductory pricing; rises to $3/$15 on 2026-09-01. Fails conference_pass 0/3.",
    ),
    Model(
        client="CandGPT4oMini",
        model_id="gpt-4o-mini",
        usd_per_1m_prompt=0.15,
        usd_per_1m_completion=0.60,
        note=(
            "Cheapest OpenAI option and nearly as fast as the incumbent, but "
            "the weakest by a distance: 83.3%, four deterministic failures."
        ),
    ),
    Model(
        client="CandGPT55",
        model_id="gpt-5.5",
        usd_per_1m_prompt=5.00,
        usd_per_1m_completion=30.00,
        note="Slowest model in the cast: 9389ms p95, 5x the incumbent.",
    ),
    Model(
        client="CandGemini36Flash",
        model_id="gemini-3.6-flash",
        usd_per_1m_prompt=1.50,
        usd_per_1m_completion=7.50,
        note="100% accurate, but 6461ms p95 — 3.5x the incumbent. 'Flash' is not fast.",
    ),
    Model(
        client="CandGemini35Flash",
        model_id="gemini-3.5-flash",
        usd_per_1m_prompt=1.50,
        usd_per_1m_completion=9.00,
        note="100% accurate. Costs MORE per output token than 3.6 Flash.",
    ),
    Model(
        client="CandGemini35FlashLite",
        model_id="gemini-3.5-flash-lite",
        usd_per_1m_prompt=0.30,
        usd_per_1m_completion=2.50,
        note="Cheapest in the cast by far — the cost-down candidate.",
    ),
]

BY_CLIENT = {m.client: m for m in [INCUMBENT, *CANDIDATES]}
