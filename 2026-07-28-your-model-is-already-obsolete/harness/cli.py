"""Throw a model at it.

    uv run python -m harness.cli --candidate CandSonnet5
    uv run python -m harness.cli --candidate CandGemini36Flash --cost-down

The whole episode in one command: run the corpus against the incumbent and
a candidate, gate the candidate against a regression budget, and either
tell you to change one string or hand the problem to the optimizer.
"""

from __future__ import annotations

import argparse
import sys

from harness.budget import COST_DOWN, SURVIVE_THE_SWAP
from harness.corpus import CORPUS
from harness.gate import gate
from harness.models import BY_CLIENT, INCUMBENT
from harness.report import Report
from harness.runner import DEFAULT_REPEATS, run


def show(report: Report, label: str) -> None:
    cost = (
        f"${report.cost_per_call * 1000:.4f}/1k calls"
        if report.cost_per_call is not None
        else "price UNVERIFIED"
    )
    print(
        f"  {label:<11} {report.model:<20} "
        f"accuracy {report.accuracy:>6.1%}   "
        f"p95 {report.p95_latency_ms:>6.0f}ms   {cost}"
    )
    for failure in report.failed_cases:
        for reason in failure.failures:
            print(f"{'':<16}  x {failure.case}: {reason}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Throw a model at it.")
    parser.add_argument("--candidate", required=True, choices=sorted(BY_CLIENT))
    parser.add_argument(
        "--repeats",
        type=int,
        default=DEFAULT_REPEATS,
        help="runs per case. Must be >= 1; these models are non-deterministic.",
    )
    parser.add_argument(
        "--cost-down",
        action="store_true",
        help="hunt for a cheaper model instead of surviving a swap",
    )
    args = parser.parse_args(argv)
    if args.repeats < 1:
        parser.error("--repeats must be >= 1; a zero-case report passes every check vacuously")

    budget = COST_DOWN if args.cost_down else SURVIVE_THE_SWAP
    mode = "COST-DOWN" if args.cost_down else "SURVIVE THE SWAP"
    print(f"\nmode: {mode}   corpus: {len(CORPUS)} cases x {args.repeats} repeats\n")

    baseline = run(INCUMBENT.client, repeats=args.repeats)
    candidate = run(args.candidate, repeats=args.repeats)
    show(baseline, "incumbent")
    show(candidate, "candidate")

    result = gate(baseline, candidate, budget)
    print()
    for check in result.checks:
        print(f"  [{'ok' if check.ok else 'XX'}] {check.name:<10} {check.detail}")

    if result.passed:
        print(f"\n  PASS — change the client string to {args.candidate} and go home.\n")
        return 0

    print(f"\n  FAIL — hand it to the optimizer:\n"
          f"      uv run python -m harness.optimize --candidate {args.candidate}\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
