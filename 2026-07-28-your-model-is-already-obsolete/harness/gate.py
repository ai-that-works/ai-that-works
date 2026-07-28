"""Should you swap? Compare a candidate to the incumbent under a budget."""

from __future__ import annotations

from dataclasses import dataclass

from harness.budget import Budget
from harness.report import Report


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str


@dataclass(frozen=True)
class GateResult:
    passed: bool
    checks: list[Check]

    @property
    def needs_optimizer(self) -> bool:
        """A failed gate means we need the optimizer."""
        return not self.passed


def _ratio(candidate: float, baseline: float) -> float:
    if baseline == 0:
        return 1.0 if candidate == 0 else float("inf")
    return candidate / baseline


def _cost_check(baseline: Report, candidate: Report, budget: Budget) -> Check:
    """Refuse to judge cost on a made-up price.

    An unverified price is not zero. Treating it as zero makes the model
    look free and hands back a confident PASS — worse than the fabricated
    price it was meant to avoid, because nothing in the output says so.
    """
    if candidate.cost_per_call is None or baseline.cost_per_call is None:
        unpriced = [r.model for r in (baseline, candidate) if r.cost_per_call is None]
        return Check(
            name="cost",
            ok=False,
            detail=(
                f"price unverified for {', '.join(unpriced)} — refusing to judge. "
                f"Add it to harness/models.py."
            ),
        )

    ratio = _ratio(candidate.cost_per_call, baseline.cost_per_call)
    return Check(
        name="cost",
        ok=ratio <= budget.max_cost_multiple,
        detail=(
            f"${candidate.cost_per_call:.6f} vs ${baseline.cost_per_call:.6f} "
            f"({ratio:.2f}x, allowed {budget.max_cost_multiple:.2f}x)"
        ),
    )


def gate(baseline: Report, candidate: Report, budget: Budget) -> GateResult:
    if not baseline.results or not candidate.results:
        raise ValueError(
            "gate() needs measured results on both sides; "
            "an empty report would pass every check vacuously"
        )

    drop = baseline.accuracy - candidate.accuracy
    latency_ratio = _ratio(candidate.p95_latency_ms, baseline.p95_latency_ms)
    cost_check = _cost_check(baseline, candidate, budget)

    checks = [
        Check(
            name="accuracy",
            ok=drop <= budget.max_accuracy_drop,
            # Report the delta from the CANDIDATE's point of view, so "+"
            # always means better. `drop` is baseline-minus-candidate and
            # inverting it here avoids a minus sign that reads as a
            # regression when the candidate has actually improved.
            detail=(
                f"{candidate.accuracy:.1%} vs {baseline.accuracy:.1%} baseline "
                # `+ 0.0` normalises -0.0, which otherwise renders as
                # "-0.0%" and reads like a defect on a projector.
                f"({-drop + 0.0:+.1%}, "
                f"allowed {-budget.max_accuracy_drop + 0.0:+.1%})"
            ),
        ),
        cost_check,
        Check(
            name="latency",
            ok=latency_ratio <= budget.max_latency_multiple,
            detail=(
                f"p95 {candidate.p95_latency_ms:.0f}ms vs "
                f"{baseline.p95_latency_ms:.0f}ms "
                f"({latency_ratio:.2f}x, allowed {budget.max_latency_multiple:.2f}x)"
            ),
        ),
    ]

    return GateResult(passed=all(c.ok for c in checks), checks=checks)
