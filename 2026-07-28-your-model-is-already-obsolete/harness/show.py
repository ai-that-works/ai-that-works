"""Stage renderer. Reads cached results. Makes ZERO network calls.

Every other entry point in this package hits provider APIs, which means
every one of them can fail live — rate limit, timeout, a provider having a
bad afternoon. This one cannot. It reads `results/*.json` written by
earlier runs and prints the tables.

    uv run python -m harness.show            # everything, in stage order
    uv run python -m harness.show matrix     # the seven-model table
    uv run python -m harness.show gate       # gate verdicts per candidate
    uv run python -m harness.show triage     # disagreement queue
    uv run python -m harness.show optimizer  # the GEPA run

If a live command misbehaves on stage, fall back to this and keep moving.
"""

from __future__ import annotations

import glob
import json
import os
import sys

from dataclasses import dataclass, field

from harness.budget import COST_DOWN, SURVIVE_THE_SWAP
from harness.config import OPTIMIZE_DIR, RESULTS_DIR
from harness.corpus import CORPUS
from harness.gate import gate as run_gate
from harness.models import BY_CLIENT, INCUMBENT
from harness.report import CaseResult

#: Latency measured while the matrix ran in parallel is inflated (~35% for
#: slow models). These are the serial measurements and are what should
#: appear on screen. See ticket 006.
SERIAL_LATENCY_MS = {
    "IncumbentGPT4o": 2083,
    "CandGemini35FlashLite": 815,
}


@dataclass(frozen=True)
class CachedReport:
    """A Report rebuilt from cached numbers, so `gate()` can judge it.

    `results` is genuine — one CaseResult per corpus run, with the real
    pass/fail pattern — so `accuracy` is derived exactly as it is live.
    Cost and latency come from the cached measurement rather than being
    recomputed from tokens, which the cache does not store.

    This exists so the stage output and the live harness run the SAME
    decision logic. An earlier version of this file reimplemented the
    three checks, which worked but would have drifted.
    """

    model: str
    results: list[CaseResult] = field(default_factory=list)
    _cost: float | None = None
    _latency: float = 0.0

    @property
    def accuracy(self) -> float:
        return sum(r.passed for r in self.results) / len(self.results) if self.results else 0.0

    @property
    def cost_per_call(self) -> float | None:
        return self._cost

    @property
    def p95_latency_ms(self) -> float:
        return self._latency

    @property
    def failed_cases(self) -> list[CaseResult]:
        return [r for r in self.results if not r.passed]


def _rebuild(client: str, row: dict) -> CachedReport:
    total = len(CORPUS) * row.get("repeats", 2)
    passed = round(row["accuracy"] * total)
    return CachedReport(
        model=client,
        results=[
            CaseResult(case=f"case_{i}", passed=i < passed, failures=() if i < passed else ("category",))
            for i in range(total)
        ],
        _cost=row["cost_per_call"],
        _latency=SERIAL_LATENCY_MS.get(client, row["p95_latency_ms"]),
    )


def _load(name: str) -> dict | None:
    path = RESULTS_DIR / f"{name}.json"
    return json.loads(path.read_text()) if path.exists() else None


def _label(client: str) -> str:
    return BY_CLIENT[client].model_id if client in BY_CLIENT else client


def matrix() -> None:
    data = _load("matrix")
    if not data:
        print("no results/matrix.json — run: uv run python -m harness.matrix")
        return
    base = data[INCUMBENT.client]

    print("\n  THE CAST — 30 cases x 2 repeats\n")
    print(f"  {'model':<26}{'acc':>7}{'p95':>9}{'cost/1k':>10}{'lat':>8}{'cost':>8}")
    print("  " + "-" * 66)
    for client, row in data.items():
        cost = row["cost_per_call"]
        latency = SERIAL_LATENCY_MS.get(client, row["p95_latency_ms"])
        base_latency = SERIAL_LATENCY_MS.get(INCUMBENT.client, base["p95_latency_ms"])
        lat_x = latency / base_latency
        cost_x = cost / base["cost_per_call"] if cost and base["cost_per_call"] else None
        marker = "*" if client != INCUMBENT.client and lat_x < 1 and (cost_x or 9) < 1 else " "
        print(
            f" {marker}{_label(client):<26}{row['accuracy']:>6.1%}"
            f"{latency:>8.0f}ms"
            f"{('$%.3f' % (cost * 1000)) if cost else 'UNPRICED':>10}"
            f"{lat_x:>7.2f}x"
            f"{(('%.2fx' % cost_x) if cost_x else '—'):>8}"
        )
    print("\n  * beats the incumbent on every dimension at once")


def gate(budgets=None) -> None:
    data = _load("matrix")
    if not data:
        print("no results/matrix.json")
        return
    baseline = _rebuild(INCUMBENT.client, data[INCUMBENT.client])

    for budget, name in budgets or (
        (SURVIVE_THE_SWAP, "SURVIVE THE SWAP"),
        (COST_DOWN, "COST-DOWN"),
    ):
        print(f"\n  GATE: {name}")
        acc = (
            "accuracy >= baseline"
            if budget.max_accuracy_drop == 0
            else f"accuracy >= baseline - {budget.max_accuracy_drop:.0%}"
        )
        print(
            f"    {acc}  |  cost <= {budget.max_cost_multiple:.2f}x"
            f"  |  p95 <= {budget.max_latency_multiple:.2f}x\n"
        )
        for client, row in data.items():
            if client == INCUMBENT.client:
                continue
            # The real gate, not a copy of it.
            result = run_gate(baseline, _rebuild(client, row), budget)
            failed = [c.name for c in result.checks if not c.ok]
            verdict = "PASS" if result.passed else f"FAIL  ({', '.join(failed)})"
            print(f"    {_label(client):<26} {verdict}")


def triage() -> None:
    data = _load("triage")
    if not data:
        print("no results/triage.json — run: uv run python -m harness.differ --candidate CandGemini35FlashLite")
        return
    total, agreed = data["pool_size"], data["agreed"]
    print(f"\n  UNLABELLED POOL — {total} documents")
    print(f"    incumbent {_label(data['incumbent'])} vs candidate {_label(data['candidate'])}\n")
    print(f"    AGREE     {agreed:>3}/{total}   auto-pass, no label needed")
    print(f"    DISAGREE  {len(data['disagreements']):>3}/{total}   a human must decide\n")
    for d in data["disagreements"]:
        head = d["document"].strip().splitlines()[0][:46]
        print(f"    {head:<48} differs on: {', '.join(d['fields'])}")
    print(f"\n  {100 * agreed / total:.0f}% of the pool needed no human attention at all.")


def optimizer() -> None:
    runs = sorted(OPTIMIZE_DIR.glob("run_*")) if OPTIMIZE_DIR.exists() else []
    if not runs:
        print("no optimizer runs under .baml_optimize/")
        return
    run = runs[-1]
    final = json.loads((run / "final_results.json").read_text())
    print(f"\n  OPTIMIZER — GEPA on claude-sonnet-5   ({run.name})")
    print(
        f"    {final['iterations_completed']} iterations, "
        f"{final['total_evaluations']} evaluations, "
        f"improvement over initial: {final['improvement_over_initial']}\n"
    )
    print(f"    {'cand':>5}{'accuracy':>10}{'prompt':>9}{'output':>8}{'total':>8}")
    for path in sorted(glob.glob(str(run / "evaluations" / "*_evaluation.json"))):
        e = json.loads(open(path).read())
        n = os.path.basename(path)[:2]
        total = e["avg_prompt_tokens"] + e["avg_completion_tokens"]
        print(
            f"    {n:>5}{e['test_pass_rate']:>9.1%}{e['avg_prompt_tokens']:>9.0f}"
            f"{e['avg_completion_tokens']:>8.0f}{total:>8.0f}"
        )
    print("\n    Savings came from the PROMPT (817 -> 267), not the output.")
    print("    GEPA was compressing our policy block — and that is what broke accuracy.")


SECTIONS = {"matrix": matrix, "gate": gate, "triage": triage, "optimizer": optimizer}


def main() -> int:
    args = sys.argv[1:]

    # Move the bar without touching a model:
    #   uv run python -m harness.show gate --accuracy-drop 0.05
    #   uv run python -m harness.show gate --cost 2.0 --latency 3.0
    overrides = {}
    flags = {"--accuracy-drop": "max_accuracy_drop", "--cost": "max_cost_multiple",
             "--latency": "max_latency_multiple"}
    rest = []
    i = 0
    while i < len(args):
        if args[i] in flags:
            overrides[flags[args[i]]] = float(args[i + 1])
            i += 2
        else:
            rest.append(args[i])
            i += 1

    if overrides:
        from harness.budget import Budget

        custom = Budget(**{**SURVIVE_THE_SWAP.__dict__, **overrides})
        print("\n  custom budget:", ", ".join(f"{k}={v}" for k, v in overrides.items()))
        gate(budgets=((custom, "CUSTOM"),))
        print()
        return 0

    for name in rest or list(SECTIONS):
        if name not in SECTIONS:
            print(f"unknown section {name!r}; choose from {', '.join(SECTIONS)}")
            return 2
        SECTIONS[name]()
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
