"""Paths, versions, and env loading — derived once, imported everywhere.

`REPO_ROOT` used to be computed two different ways (`parents[2]` in the
runner, `parents[1]` in the optimizer). Both were right until someone
moved a folder, at which point exactly one would break.
"""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

#: This episode's folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

#: The ai-that-works repo root, where the shared .env lives.
REPO_ROOT = PROJECT_ROOT.parent

BAML_SRC = PROJECT_ROOT / "baml_src"
EXPENSE_BAML = BAML_SRC / "expense.baml"
GENERATED_TESTS_BAML = BAML_SRC / "generated_tests.baml"
OPTIMIZE_DIR = PROJECT_ROOT / ".baml_optimize"
POOL_PATH = PROJECT_ROOT / "data" / "unlabelled_pool.txt"
RESULTS_DIR = PROJECT_ROOT / "results"

#: Must match `version` in baml_src/generators.baml and the baml-py pin in
#: pyproject.toml — baml-cli hard-fails on a mismatch.
BAML_VERSION = "0.223.0"

BAML_CLI = ["uv", "run", "--no-project", "--with", f"baml-py=={BAML_VERSION}", "baml-cli"]

DOTENV_PATH = REPO_ROOT / ".env"


def load_env() -> None:
    """Load the repo-root .env. Idempotent; never overrides a real env var."""
    load_dotenv(DOTENV_PATH, override=False)
