"""Run the prompt optimizer against a candidate model.

The optimizer is a BLACK BOX we call. How GEPA works was covered in
2025-12-16-prompt-optimizer; this episode owes no explanation of it.

SWAP MECHANISM #2 of 2, and the least elegant part of the system.
`baml-cli` is a Rust binary that reads `baml_src/` off disk, so the Python
`ClientRegistry` trick in `runner.py` is invisible to it. There is no
`--model` flag. The client declared in the .baml file IS the target. So to
optimize a prompt for a candidate, we rewrite the file, run the optimizer,
and put the file back.

That asymmetry is worth showing on the diagram rather than hiding: it is
exactly the kind of seam that appears when you compose real tools.

Operational notes, all learned by running it (see ticket 009):
  * `--beta` is mandatory; it exits(1) without it.
  * The default `--max-evals 50` HARD-ERRORS on small corpora. It must be
    at least (trials + 1) * num_tests.
  * It blocks on stdin at the end even with `--no-ui`, and it wants a
    CANDIDATE ID, not a confirmation. `echo y |` does not work.
  * Artifacts land in `.baml_optimize/run_*/` as subdirectories.
"""

from __future__ import annotations

import re
import subprocess
from contextlib import contextmanager
from pathlib import Path

from harness.budget import Budget
from harness.config import (
    BAML_CLI,
    BAML_SRC,
    DOTENV_PATH,
    EXPENSE_BAML,
    OPTIMIZE_DIR,
    PROJECT_ROOT,
)


@contextmanager
def client_pinned_to(client: str):
    """Temporarily rewrite the function's client, then restore it.

    Restores on the way out even if the optimizer explodes — leaving the
    source pinned to a candidate would silently change what every later
    run measures.
    """
    original = EXPENSE_BAML.read_text()
    swapped = re.sub(
        r"^(\s*)client\s+\w+\s*$",
        rf"\g<1>client {client}",
        original,
        count=1,
        flags=re.MULTILINE,
    )
    if swapped == original:
        raise RuntimeError(
            f"could not find a `client <Name>` line to rewrite in {EXPENSE_BAML}"
        )
    try:
        EXPENSE_BAML.write_text(swapped)
        yield
    finally:
        EXPENSE_BAML.write_text(original)


def optimize(
    client: str,
    budget: Budget,
    *,
    num_tests: int | None = None,
    trials: int = 6,
    auto: str = "light",
) -> Path:
    """Optimize the prompt for `client`. Returns the run directory.

    Regenerates the BAML test blocks first. `baml-cli optimize` reads its
    corpus from `test` blocks on disk and nothing else — with none present
    it completes happily against zero tests and improves nothing.
    """
    from harness.testgen import write as write_tests

    written = write_tests()
    num_tests = num_tests or written
    if not num_tests:
        raise RuntimeError("corpus is empty — the optimizer would have nothing to score")

    # The default --max-evals of 50 HARD-ERRORS on small corpora.
    max_evals = (trials + 1) * num_tests

    with client_pinned_to(client):
        subprocess.run(
            [
                *BAML_CLI, "optimize",
                "--beta",
                "--from", str(BAML_SRC),
                "--function", "ExtractExpense",
                "--auto", auto,
                "--max-evals", str(max_evals),
                "--weight", budget.to_optimizer_weights(),
                "--no-ui",
                "--dotenv-path", str(DOTENV_PATH),
            ],
            # It asks for a candidate id at the end. Empty input = skip
            # applying; artifacts are already on disk either way.
            input="\n",
            text=True,
            check=True,
            cwd=PROJECT_ROOT,
        )

    runs = sorted(OPTIMIZE_DIR.glob("run_*"))
    if not runs:
        raise RuntimeError("optimizer produced no run directory")
    return runs[-1]


def _main() -> int:
    import argparse

    from harness.budget import COST_DOWN, SURVIVE_THE_SWAP
    from harness.models import BY_CLIENT

    parser = argparse.ArgumentParser(description="Repair a prompt for a candidate model.")
    parser.add_argument("--candidate", required=True, choices=sorted(BY_CLIENT))
    parser.add_argument("--cost-down", action="store_true")
    parser.add_argument("--auto", default="light", choices=["light", "medium", "heavy"])
    args = parser.parse_args()

    budget = COST_DOWN if args.cost_down else SURVIVE_THE_SWAP
    print(f"optimizing for {args.candidate}, weights: {budget.to_optimizer_weights()}")
    run_dir = optimize(args.candidate, budget, auto=args.auto)
    print(f"\nartifacts: {run_dir}")
    print(f"replay:    {replay_command(run_dir)}")
    return 0


def replay_command(run_dir: Path) -> str:
    """The stage command: replays a finished run in the TUI, zero tokens.

    Needs a real TTY — it fails with "Device not configured" when piped.
    VERIFY THIS ON THE PRESENTATION MACHINE before depending on it live.
    """
    return f"baml-cli optimize --view --run-dir {run_dir}"


if __name__ == "__main__":
    raise SystemExit(_main())
