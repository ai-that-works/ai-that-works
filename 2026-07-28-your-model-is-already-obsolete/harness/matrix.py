"""Every model against the whole corpus. The episode's headline table.

    uv run python -m harness.matrix [--repeats N]

Repeats are not optional. These models are non-deterministic on this task
and single-sample runs produced two confidently wrong conclusions during
development — first "the task is saturated", then "the trap catches
models". Both were noise.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from harness.config import PROJECT_ROOT
from harness.models import CANDIDATES, INCUMBENT
from harness.runner import run

RESULTS_JSON = PROJECT_ROOT / "results" / "matrix.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=2)
    args = parser.parse_args()

    cast = [INCUMBENT, *CANDIDATES]
    print(f"\n{'model':<20} {'acc':>7} {'p95':>8} {'cost/1k':>10}  failures")
    print("-" * 88)

    # Embarrassingly parallel: models do not interact and neither do cases
    # within a model. Sequentially this is sum-of-all-models; in a pool it
    # is bounded by the slowest single model. 360 calls went from ~12min
    # to ~2min.
    with ThreadPoolExecutor(max_workers=len(cast)) as pool:
        futures = {
            model.client: pool.submit(run, model.client, args.repeats)
            for model in cast
        }
        reports = {client: f.result() for client, f in futures.items()}

    for model in cast:
        report = reports[model.client]
        cost = (
            f"${report.cost_per_call * 1000:.3f}"
            if report.cost_per_call is not None
            else "UNPRICED"
        )
        counts = Counter(f.case for f in report.failed_cases)
        summary = ", ".join(
            f"{name}({n}/{args.repeats})" for name, n in counts.most_common(4)
        )
        print(
            f"{model.client:<20} {report.accuracy:>6.1%} "
            f"{report.p95_latency_ms:>7.0f}ms {cost:>10}  {summary or 'clean'}"
        )

    print("\nfailure reasons by model:")
    for client, report in reports.items():
        reasons = {f.failures[0] for f in report.failed_cases if f.failures}
        for reason in sorted(reasons):
            print(f"  {client:<20} {reason}")

    # Persist so downstream work (the gate, 007's walkthrough) does not
    # have to pay for these measurements again.
    RESULTS_JSON.parent.mkdir(exist_ok=True)
    RESULTS_JSON.write_text(
        json.dumps(
            {
                client: {
                    "accuracy": r.accuracy,
                    "p95_latency_ms": r.p95_latency_ms,
                    "cost_per_call": r.cost_per_call,
                    "repeats": args.repeats,
                    "failures": sorted(
                        {f"{f.case}: {f.failures[0]}" for f in r.failed_cases if f.failures}
                    ),
                }
                for client, r in reports.items()
            },
            indent=2,
        )
    )
    print(f"\nwrote {RESULTS_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
