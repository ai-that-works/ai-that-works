"""The gate's spec, written before the gate.

`harness/gate.py` is typed live on stage. To reproduce the segment, delete
it and run this suite: `importorskip` keeps the rest of the tests green
while it is absent, and all of these light up once it is back.

The reference implementation ships in the repo — the audience wants the
code, and a spec nobody has proven satisfiable is how you end up with an
assertion no output can pass.

Run:  uv run pytest -q
"""

from __future__ import annotations

import pytest

from harness.budget import COST_DOWN, SURVIVE_THE_SWAP, Budget
from harness.report import CaseResult, Report

gate_module = pytest.importorskip(
    "harness.gate",
    reason="gate.py is written live on stage — that's the point",
)
gate = gate_module.gate


def report(
    model: str,
    *,
    passed: int,
    total: int,
    prompt_tokens: int = 200,
    completion_tokens: int = 150,
    latency_ms: float = 1000.0,
    usd_in: float | None = 2.50,
    usd_out: float | None = 10.00,
) -> Report:
    results = [
        CaseResult(
            case=f"case_{i}",
            passed=i < passed,
            failures=() if i < passed else ("category",),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
        )
        for i in range(total)
    ]
    return Report(
        model=model,
        results=results,
        usd_per_1m_prompt=usd_in,
        usd_per_1m_completion=usd_out,
    )


BASELINE = report("gpt-4o", passed=30, total=30)


class TestAccuracy:
    def test_identical_candidate_passes(self):
        assert gate(BASELINE, report("cand", passed=30, total=30), SURVIVE_THE_SWAP).passed

    def test_any_accuracy_regression_fails_by_default(self):
        """max_accuracy_drop=0.0 means exactly that. One case is enough."""
        result = gate(BASELINE, report("cand", passed=29, total=30), SURVIVE_THE_SWAP)
        assert not result.passed

    def test_more_accurate_candidate_passes(self):
        worse_baseline = report("gpt-4o", passed=25, total=30)
        assert gate(worse_baseline, report("cand", passed=30, total=30), SURVIVE_THE_SWAP).passed

    def test_regression_within_an_explicit_allowance_passes(self):
        lenient = Budget(max_accuracy_drop=0.05)
        # 29/30 is a 3.3pp drop, inside a 5pp allowance.
        assert gate(BASELINE, report("cand", passed=29, total=30), lenient).passed


class TestCost:
    def test_cheaper_candidate_passes(self):
        cheap = report("cand", passed=30, total=30, usd_in=0.30, usd_out=2.50)
        assert gate(BASELINE, cheap, SURVIVE_THE_SWAP).passed

    def test_cost_beyond_the_multiple_fails(self):
        pricey = report("cand", passed=30, total=30, usd_in=25.0, usd_out=100.0)
        assert not gate(BASELINE, pricey, SURVIVE_THE_SWAP).passed

    def test_cost_within_the_multiple_passes(self):
        # 1.1x the incumbent, inside the default 1.2x allowance.
        slightly = report("cand", passed=30, total=30, usd_in=2.75, usd_out=11.0)
        assert gate(BASELINE, slightly, SURVIVE_THE_SWAP).passed

    def test_more_verbose_model_costs_more_even_at_the_same_price(self):
        """Cost is price x tokens. A chattier model is a more expensive one."""
        chatty = report("cand", passed=30, total=30, completion_tokens=900)
        assert not gate(BASELINE, chatty, SURVIVE_THE_SWAP).passed


class TestLatency:
    def test_slower_beyond_the_multiple_fails(self):
        slow = report("cand", passed=30, total=30, latency_ms=4000.0)
        assert not gate(BASELINE, slow, SURVIVE_THE_SWAP).passed

    def test_faster_candidate_passes(self):
        fast = report("cand", passed=30, total=30, latency_ms=400.0)
        assert gate(BASELINE, fast, SURVIVE_THE_SWAP).passed


class TestUnverifiedPrices:
    """A price we haven't verified is NOT zero.

    This had no coverage, and the bug it hid was a guaranteed false PASS:
    `None` was coerced to 0.0, cost came out at 0.00x, and the check went
    green for four of five candidates — including the one the README uses
    for the cost-down demo.
    """

    def test_unpriced_candidate_cannot_pass(self):
        unpriced = report("cand", passed=30, total=30, usd_in=None, usd_out=None)
        assert not gate(BASELINE, unpriced, SURVIVE_THE_SWAP).passed

    def test_unpriced_candidate_cannot_pass_cost_down_either(self):
        unpriced = report("cand", passed=30, total=30, usd_in=None, usd_out=None)
        assert not gate(BASELINE, unpriced, COST_DOWN).passed

    def test_it_says_the_price_is_the_problem(self):
        unpriced = report("cand", passed=30, total=30, usd_in=None, usd_out=None)
        result = gate(BASELINE, unpriced, SURVIVE_THE_SWAP)
        cost = next(c for c in result.checks if c.name == "cost")
        assert not cost.ok
        assert "unverified" in cost.detail.lower()
        assert "cand" in cost.detail

    def test_an_unpriced_baseline_is_also_refused(self):
        unpriced_baseline = report("gpt-4o", passed=30, total=30, usd_in=None, usd_out=None)
        result = gate(unpriced_baseline, report("cand", passed=30, total=30), SURVIVE_THE_SWAP)
        assert not result.passed

    def test_accuracy_and_latency_still_judged_normally(self):
        """Refusing to price must not suppress the other two dimensions."""
        unpriced = report("cand", passed=30, total=30, usd_in=None, usd_out=None)
        result = gate(BASELINE, unpriced, SURVIVE_THE_SWAP)
        assert next(c for c in result.checks if c.name == "accuracy").ok
        assert next(c for c in result.checks if c.name == "latency").ok


class TestEmptyReports:
    """A zero-case report used to pass every check vacuously."""

    def test_empty_candidate_raises(self):
        with pytest.raises(ValueError):
            gate(BASELINE, Report(model="cand", results=[]), SURVIVE_THE_SWAP)

    def test_empty_baseline_raises(self):
        with pytest.raises(ValueError):
            gate(Report(model="gpt-4o", results=[]), BASELINE, SURVIVE_THE_SWAP)


class TestCostDownMode:
    """Same gate, inverted budget. The harness pays for itself twice."""

    def test_merely_as_cheap_is_not_good_enough(self):
        same = report("cand", passed=30, total=30)
        assert not gate(BASELINE, same, COST_DOWN).passed

    def test_genuinely_cheaper_at_equal_quality_passes(self):
        cheap = report("cand", passed=30, total=30, usd_in=0.30, usd_out=2.50)
        assert gate(BASELINE, cheap, COST_DOWN).passed

    def test_cheap_but_worse_still_fails(self):
        cheap_dumb = report("cand", passed=27, total=30, usd_in=0.10, usd_out=0.40)
        assert not gate(BASELINE, cheap_dumb, COST_DOWN).passed


class TestExplainsItself:
    """A gate that says 'no' without saying why is a coin flip."""

    def test_reports_every_dimension_checked(self):
        result = gate(BASELINE, report("cand", passed=30, total=30), SURVIVE_THE_SWAP)
        assert {c.name for c in result.checks} == {"accuracy", "cost", "latency"}

    def test_names_the_dimension_that_failed(self):
        slow = report("cand", passed=30, total=30, latency_ms=9000.0)
        result = gate(BASELINE, slow, SURVIVE_THE_SWAP)
        failed = [c.name for c in result.checks if not c.ok]
        assert failed == ["latency"]

    def test_a_failing_check_carries_the_numbers(self):
        slow = report("cand", passed=30, total=30, latency_ms=9000.0)
        result = gate(BASELINE, slow, SURVIVE_THE_SWAP)
        detail = next(c.detail for c in result.checks if c.name == "latency")
        assert "9000" in detail and "1000" in detail

    def test_an_improvement_is_not_shown_as_a_minus(self):
        """A better candidate must not read like a regression on stage."""
        worse_baseline = report("gpt-4o", passed=15, total=30)
        result = gate(worse_baseline, report("cand", passed=30, total=30), SURVIVE_THE_SWAP)
        detail = next(c.detail for c in result.checks if c.name == "accuracy")
        assert "+50.0%" in detail

    def test_no_negative_zero_in_the_output(self):
        """-0.0% reads like a defect on a projector."""
        result = gate(BASELINE, report("cand", passed=30, total=30), SURVIVE_THE_SWAP)
        detail = next(c.detail for c in result.checks if c.name == "accuracy")
        assert "-0.0%" not in detail

    def test_multiple_failures_all_reported(self):
        awful = report(
            "cand", passed=20, total=30, latency_ms=9000.0, usd_in=99.0, usd_out=99.0
        )
        result = gate(BASELINE, awful, SURVIVE_THE_SWAP)
        assert sum(not c.ok for c in result.checks) == 3


class TestTheDecision:
    """PASS -> swap the string. FAIL -> run the optimizer."""

    def test_pass_means_ship_it(self):
        result = gate(BASELINE, report("cand", passed=30, total=30), SURVIVE_THE_SWAP)
        assert result.passed and not result.needs_optimizer

    def test_fail_routes_to_the_optimizer(self):
        result = gate(BASELINE, report("cand", passed=25, total=30), SURVIVE_THE_SWAP)
        assert not result.passed and result.needs_optimizer
