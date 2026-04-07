# Offline indexer. Run this to rebuild the search indexes:
#   python index.py
#
# Produces two files consumed by fusion.py and oracle.py at query time:
#   docfreq.json  — document frequency table (term -> number of episodes containing it)
#                   Used to compute IDF weights for ranking search results.
#   symbols.json  — set of code identifiers (camelCase/snake_case names) found in the repo.
#                   Used by oracle.py to distinguish code symbol queries from topic queries.

import json
import re
from collections import defaultdict
from pathlib import Path

from fusion import CODE_EXTENSIONS, CODE_STRUCTURAL, REPO_ROOT, DATA_JSON

INDEX_DIR = Path(__file__).resolve().parent
# Matches valid programming identifiers
IDENTIFIER_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")


# Build docfreq.json: for each episode, tokenize its title + description + transcript,
# then count how many episodes contain each unique term.
def build_docfreq():
    episodes = json.loads(DATA_JSON.read_text())["episodes"]
    df = defaultdict(int)
    n = len(episodes)
    for ep in episodes:
        folder = ep["folder"]
        parts = [ep.get("title", ""), ep.get("description", "")]
        ep_dir = REPO_ROOT / folder
        for pattern in ["transcript.md", "transcript.txt"]:
            tf = ep_dir / pattern
            if tf.is_file():
                parts.append(tf.read_text(errors="ignore"))
        text = " ".join(parts).lower()
        seen = set(re.findall(r"[a-z0-9]+", text))
        for term in seen:
            df[term] += 1
    result = {"_n": n}
    result.update(df)
    path = INDEX_DIR / "docfreq.json"
    path.write_text(json.dumps(result))
    print(f"Document frequencies: {len(df)} terms across {n} episodes -> {path}")


# Build symbols.json: scan all code files in episode directories for identifiers
# that look like code (camelCase, snake_case, etc.) and collect them into a set.
def build_symbols():
    symbols = set()
    for ep_dir in sorted(REPO_ROOT.iterdir()):
        if not ep_dir.is_dir() or not re.match(r"\d{4}-\d{2}-\d{2}-.+", ep_dir.name):
            continue
        for ext in CODE_EXTENSIONS:
            for cf in ep_dir.rglob(f"*{ext}"):
                try:
                    text = cf.read_text(errors="ignore")
                except OSError:
                    continue
                for ident in IDENTIFIER_RE.findall(text):
                    if CODE_STRUCTURAL.search(ident):
                        symbols.add(ident)
    path = INDEX_DIR / "symbols.json"
    path.write_text(json.dumps(sorted(symbols)))
    print(f"Code symbols: {len(symbols)} identifiers -> {path}")


def main():
    build_docfreq()
    build_symbols()
    print("Done.")


if __name__ == "__main__":
    main()
