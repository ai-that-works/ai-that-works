"""Where test cases come from.

Random production sampling means labelling ~200 easy cases to find three
interesting ones. Differential sampling means nearly everything a human
touches is load-bearing.

The trick: under a RELATIVE gate, you are not asking "is this output
correct?" — you are asking "is this no worse than what I run today?" For
that question the incumbent IS the reference. Where incumbent and candidate
agree, the swap changes nothing observable in production, so the case needs
no label at all. Only disagreements can alter behaviour, so only
disagreements go to a human.

The caveat, which must be said out loud on stage: this buys RELATIVE
safety, not absolute quality. If the incumbent is quietly wrong about
something, agreement will migrate that wrongness forever. That is why the
anchor set in `corpus.py` exists — a small hand-labelled tier that keeps
you honest about absolute quality.
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from harness.config import POOL_PATH, load_env
from harness.corpus import Case
from harness.runner import run_case


@dataclass(frozen=True)
class Disagreement:
    """One unlabelled document the two models answered differently."""

    document: str
    incumbent_output: str
    candidate_output: str
    fields: tuple[str, ...]

    def summary(self) -> str:
        head = self.document.strip().splitlines()[0][:48]
        return f"{head:<50} differs on: {', '.join(self.fields)}"


def _comparable(output_json: str) -> dict:
    """The fields whose disagreement would change production behaviour."""
    data = json.loads(output_json)
    return {
        "category": data.get("category"),
        "total": data.get("total"),
        "tax": data.get("tax"),
        "n_items": len(data.get("line_items") or []),
    }


def diff(document: str, incumbent: str, candidate: str) -> Disagreement | None:
    """Run both models on one unlabelled document. None if they agree."""
    # No gold: nothing is scored on this path, the two outputs are only
    # compared to each other. That is the whole point — an unlabelled
    # document has no right answer until a human supplies one.
    probe = Case(name="unlabelled", document=document, gold=None)
    incumbent_result = run_case(probe, incumbent)
    candidate_result = run_case(probe, candidate)

    if not incumbent_result.output or not candidate_result.output:
        return Disagreement(
            document, incumbent_result.output, candidate_result.output, ("error",)
        )

    incumbent_fields = _comparable(incumbent_result.output)
    candidate_fields = _comparable(candidate_result.output)
    differing = tuple(
        field for field in incumbent_fields
        if incumbent_fields[field] != candidate_fields[field]
    )
    if not differing:
        return None

    return Disagreement(
        document, incumbent_result.output, candidate_result.output, differing
    )


def triage(
    pool: list[str], incumbent: str, candidate: str, workers: int = 8
) -> list[Disagreement]:
    """Sort an unlabelled pool into 'ignore' and 'a human must look'."""
    load_env()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        found = list(executor.map(lambda d: diff(d, incumbent, candidate), pool))
    return [d for d in found if d is not None]


def load_pool(path: Path | None = None) -> list[str]:
    """Unlabelled documents, one per `---` separated block."""
    return [
        block.strip()
        for block in (path or POOL_PATH).read_text().split("\n---\n")
        if block.strip()
    ]


def _main() -> int:
    import argparse

    from harness.models import BY_CLIENT, INCUMBENT

    parser = argparse.ArgumentParser(
        description="Triage an unlabelled pool: agreements are free, disagreements need a human."
    )
    parser.add_argument("--candidate", required=True, choices=sorted(BY_CLIENT))
    parser.add_argument("--incumbent", default=INCUMBENT.client, choices=sorted(BY_CLIENT))
    args = parser.parse_args()

    pool = load_pool()
    print(f"\n{len(pool)} unlabelled documents")
    print(f"  incumbent: {args.incumbent}")
    print(f"  candidate: {args.candidate}\n")

    disagreements = triage(pool, args.incumbent, args.candidate)
    agreed = len(pool) - len(disagreements)

    print(f"  AGREE     {agreed:>3}/{len(pool)}  -> auto-pass, no label needed")
    print(f"  DISAGREE  {len(disagreements):>3}/{len(pool)}  -> queue for a human\n")

    if disagreements:
        print("a human needs to adjudicate these:")
        for d in disagreements:
            print(f"  {d.summary()}")

    # Persist for the stage walkthrough — re-running costs 2 calls per
    # document and the answer does not change.
    from harness.config import RESULTS_DIR

    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "triage.json").write_text(
        json.dumps(
            {
                "incumbent": args.incumbent,
                "candidate": args.candidate,
                "pool_size": len(pool),
                "agreed": agreed,
                "disagreements": [
                    {
                        "document": d.document,
                        "fields": list(d.fields),
                        "incumbent_output": d.incumbent_output,
                        "candidate_output": d.candidate_output,
                    }
                    for d in disagreements
                ],
            },
            indent=2,
        )
    )

    saved = 100 * agreed / len(pool) if pool else 0
    print(
        f"\n{saved:.0f}% of the pool needed no human attention at all. "
        "That is the whole argument for differential sampling:\n"
        "under a relative gate, an agreement means the swap changes nothing\n"
        "observable, so there is nothing to label."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
