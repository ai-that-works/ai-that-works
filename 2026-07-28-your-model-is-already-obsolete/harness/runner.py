"""Run the corpus against one model and produce a Report.

SWAP MECHANISM #1 of 2: `ClientRegistry` overrides the model at RUNTIME.
No file edits, no regeneration, no code change per model. This is the
"throw a model at it" claim, and it is the entire reason evaluation is
cheap enough to do on every candidate.

(Mechanism #2 lives in `optimize.py` and is uglier, because `baml-cli` is a
Rust binary that cannot see a Python registry. See that module.)

Validators are deterministic — pure Python comparisons against gold. No
LLM-as-judge: no extra API cost, no non-determinism in the scorer itself,
no model grading its own homework.
"""

from __future__ import annotations

import time

from baml_client import b
from baml_py import ClientRegistry, Collector

from harness.config import load_env
from harness.corpus import CORPUS, Case
from harness.models import BY_CLIENT
from harness.report import CaseResult, Report

#: Models are non-deterministic on this task. A single sample per case
#: produced two wrong conclusions during design. Always repeat.
DEFAULT_REPEATS = 3


def validate(expense, case: Case) -> tuple[str, ...]:
    """Deterministic checks. Returns the names of what failed."""
    gold = case.gold
    if gold is None:
        # Unlabelled document on the differential path — nothing to score
        # against. differ.py compares the two outputs to each other.
        return ()

    failures: list[str] = []

    if expense.category.value != gold.category:
        failures.append(f"category: expected {gold.category}, got {expense.category.value}")
    if gold.tax_is_none and expense.tax is not None:
        failures.append(f"tax: expected omitted, got {expense.tax}")
    if not gold.tax_is_none and expense.tax is None:
        failures.append("tax: expected a value, got omitted")
    if abs(expense.total - gold.total) > 0.01:
        failures.append(f"total: expected {gold.total}, got {expense.total}")
    if len(expense.line_items) != gold.n_items:
        failures.append(f"line_items: expected {gold.n_items}, got {len(expense.line_items)}")
    for item in expense.line_items:
        if abs(item.quantity * item.unit_price - item.total) > 0.01:
            failures.append(f"line maths: {item.description!r} does not reconcile")
            break

    return tuple(failures)


def run_case(case: Case, client: str) -> CaseResult:
    registry = ClientRegistry()
    registry.set_primary(client)
    collector = Collector(name=client)

    started = time.perf_counter()
    try:
        expense = b.ExtractExpense(
            case.document,
            baml_options={"client_registry": registry, "collector": collector},
        )
    except Exception as exc:  # noqa: BLE001
        return CaseResult(
            case=case.name,
            passed=False,
            failures=(f"{type(exc).__name__}: {exc}",),
            latency_ms=(time.perf_counter() - started) * 1000,
        )

    latency_ms = (time.perf_counter() - started) * 1000
    failures = validate(expense, case)

    prompt_tokens = completion_tokens = 0
    try:
        usage = collector.last.usage
        prompt_tokens = usage.input_tokens or 0
        completion_tokens = usage.output_tokens or 0
    except Exception:  # noqa: BLE001
        pass

    return CaseResult(
        case=case.name,
        passed=not failures,
        failures=failures,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        latency_ms=latency_ms,
        output=expense.model_dump_json(),
    )


def run(client: str, repeats: int = DEFAULT_REPEATS, cases: list[Case] | None = None) -> Report:
    """Throw one model at the corpus."""
    if repeats < 1:
        raise ValueError(f"repeats must be >= 1, got {repeats}")
    load_env()
    model = BY_CLIENT[client]
    results = [
        run_case(case, client)
        for case in (cases or CORPUS)
        for _ in range(repeats)
    ]
    # Prices stay `None` when unverified. Do NOT coerce to 0.0 — see the
    # note on Report.usd_per_1m_prompt.
    return Report(
        model=client,
        results=results,
        usd_per_1m_prompt=model.usd_per_1m_prompt,
        usd_per_1m_completion=model.usd_per_1m_completion,
    )
