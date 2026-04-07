import json
import math
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Grep Fusion — the retrieval engine behind oracle.
#
# Searches the podcast repo using three independent sources:
#   structured() — substring match against episode titles/descriptions in data.json
#   transcript() — regex search across transcript.md/txt files
#   code()       — regex search across .py/.ts/.tsx/.baml code files
#   topics()     — match query terms against topic words parsed from folder names
#
# Each source produces a ranked list of episode matches scored by IDF-weighted
# term hits. search() runs all 4, then rrf() merges them using Reciprocal Rank
# Fusion — episodes appearing in multiple sources get boosted, noise gets filtered.
# A lightweight rerank() pass then rescores using title overlap, recency, and
# description density before returning final results.

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_JSON = REPO_ROOT / "data.json"

# Detects code-like tokens: camelCase, snake_case, or alphanumeric mixes.
# Shared between oracle.py (query-time classification) and index.py (index-time extraction).
CODE_STRUCTURAL = re.compile(r"[a-z][A-Z]|_|[a-z]\d|\d[a-z]")

# Tokenizer matching index.py's docfreq builder — lowercase alphanumeric runs.
# Used in idf() to split compound terms that aren't in the index directly.
TOKENIZE_RE = re.compile(r"[a-z0-9]+")

# RRF parameters (Cormack et al., 2009)
RRF_K = 60             # smoothing constant — higher = less penalty for lower ranks
RRF_SCORE_FLOOR = 0.3  # drop results scoring below 30% of the top result
RRF_MIN_SCORE = 0.01   # absolute floor: skip near-zero matches from noisy queries

# BM25 saturation constant: tf / (tf + k). Higher k = slower saturation.
# At k=1.5: tf=1 scores 0.4, tf=2 scores 0.57, tf=5 scores 0.77, tf=50 scores 0.97
BM25_K = 1.5
# Merge transcript blocks whose line ranges are within this gap
BLOCK_MERGE_GAP = 5
# Keep top-N blocks per episode before merging
BLOCKS_PER_EPISODE = 4


# Timestamp formats found in transcripts:
#   "(12:34)" — parenthesized mm:ss used in .md transcripts
#   "00:12:34,567 -->" — WebVTT format used in .txt transcripts
TIMESTAMP_RE = re.compile(r"\((\d{1,2}):(\d{2})(?:\.\d+)?\)")
VTT_RE = re.compile(r"(\d{2}):(\d{2}):(\d{2})[\.,]\d{3}\s*-->")
# Episode directories are named like "2025-06-17-entity-extraction"
EPISODE_DIR_RE = re.compile(r"\d{4}-\d{2}-\d{2}-.+")

# Document frequency table built by index.py. Maps term -> number of episodes
# containing that term. Used to compute IDF weights.
_docfreq_cache = None


def load_docfreq() -> tuple[dict[str, int], int]:
    global _docfreq_cache
    if _docfreq_cache is not None:
        return _docfreq_cache
    path = Path(__file__).resolve().parent / "docfreq.json"
    if not path.exists():
        print("warning: docfreq.json missing — IDF weighting disabled. Run index.py to build it.", file=sys.stderr)
        _docfreq_cache = ({}, 1)
        return _docfreq_cache
    raw = json.loads(path.read_text())
    n = raw.get("_n", 1)
    df = {k: v for k, v in raw.items() if k != "_n"}
    _docfreq_cache = (df, n)
    return _docfreq_cache


# Inverse Document Frequency: log(N / (1 + df)), clamped to 0.
# Rare terms get high scores, common terms (appearing in every episode) get ~0.
# Used both for filtering (IDF_FLOOR in oracle.py) and weighting search hits.
#
# Compound terms (e.g. "snake_case") that aren't in the index are split into
# sub-tokens using the same tokenizer as index.py. The highest document frequency
# among sub-tokens is used, preventing compound terms from being treated as
# maximally rare just because the indexer split them differently.
def idf(term: str) -> float:
    df, n = load_docfreq()
    low = term.lower()
    count = df.get(low, 0)
    if count == 0:
        parts = TOKENIZE_RE.findall(low)
        if len(parts) > 1:
            count = max(df.get(p, 0) for p in parts)
    return max(0, math.log(n / (1 + count)))


# Extract the first timestamp from a text block, returned as total seconds.
# Tries parenthesized format first, then WebVTT.
def extract_timestamp(text: str) -> int | None:
    for m in TIMESTAMP_RE.finditer(text):
        return int(m.group(1)) * 60 + int(m.group(2))
    for m in VTT_RE.finditer(text):
        return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
    return None


def format_timestamp(seconds: int) -> str:
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


# Generate a regex pattern that matches morphological variants of a term.
# "eval" -> \bevals?\b|\bevaluat\w*\b  (catches eval, evals, evaluate, evaluation, etc.)
# "classify" -> \bclassif\w*\b  (catches classify, classification, classifier, etc.)
STEM_SUFFIXES = {
    "e": (3, r"\w*"),       # "configure" -> "configur\w*"
    "y": (3, r"(?:y|ies|ying|ied|ication|ier)\b"),
    "ing": (3, r"(?:ing|e|ed|er|es)?\b"),
    "tion": (3, r"(?:tion|te|ting|ted|tes)?\b"),
    "ed": (3, r"(?:ed|e|ing|er|es)?\b"),
    "er": (3, r"(?:er|e|ing|ed|es)?\b"),
    "s": (3, r"(?:s|ed|ing|er)?\b"),
}


def morpho(term: str) -> str:
    low = term.lower()
    if len(low) < 4:
        return r'\b' + re.escape(low) + r's?\b'
    # Try to find the longest matching suffix
    for suffix, (min_stem, replacement) in sorted(STEM_SUFFIXES.items(), key=lambda x: len(x[0]), reverse=True):
        if low.endswith(suffix) and len(low) - len(suffix) >= min_stem:
            stem = re.escape(low[:-len(suffix)])
            return r'\b' + stem + replacement
    # Default: allow optional trailing characters
    return r'\b' + re.escape(low) + r's?\b|\b' + re.escape(low[:max(4, len(low)-2)]) + r'\w*\b'


def merge_blocks(blocks: list[tuple[float, int, int, str, int]], gap: int = BLOCK_MERGE_GAP) -> list[tuple[float, int, int, str, int]]:
    if not blocks:
        return []
    blocks.sort(key=lambda b: b[1])
    merged = [blocks[0]]
    for score, start, end, text, line_hit in blocks[1:]:
        prev_score, prev_start, prev_end, prev_text, prev_line = merged[-1]
        if start <= prev_end + gap:
            new_start = prev_start
            new_end = max(prev_end, end)
            new_score = prev_score + score
            new_text = prev_text  # will be re-extracted
            new_line = prev_line
            merged[-1] = (new_score, new_start, new_end, new_text, new_line)
        else:
            merged.append((score, start, end, text, line_hit))
    return merged


# A single episode match from one retrieval source.
@dataclass
class Match:
    folder: str     # episode directory name, e.g. "2025-06-17-entity-extraction"
    title: str
    snippet: str    # best matching text from this source
    source: str     # which source produced this: "structured", "transcript", or "code"
    line: int | None = None        # line number in the matched file
    file: str | None = None        # relative path to the matched file
    links: dict = field(default_factory=dict)  # youtube, etc. from data.json
    source_count: int = 1          # how many sources agreed on this episode (set by rrf)
    timestamp: int | None = None   # seconds into episode, extracted from transcript


# Final merged result after RRF fusion.
@dataclass
class FusionResult:
    matches: list[Match]           # ranked episodes, best first
    scores: dict[str, float]       # folder -> RRF score (for debugging/gating)


def load_episodes() -> list[dict]:
    return json.loads(DATA_JSON.read_text())["episodes"]


# --- Source 1: Structured metadata ---
# Searches episode titles and descriptions from data.json.
# Scores each episode by sum of IDF weights for matching terms.
# No per-source threshold — RRF handles final ranking and gating.
def structured(terms: list[str], episodes: list[dict] | None = None) -> list[Match]:
    if episodes is None:
        episodes = load_episodes()
    patterns = [(re.compile(morpho(t), re.IGNORECASE), idf(t)) for t in terms]
    scored = []
    for ep in episodes:
        text = f"{ep.get('title', '')} {ep.get('description', '')}".lower()
        score = 0
        for pat, w in patterns:
            tf = len(pat.findall(text))
            if tf > 0:
                score += w * (tf / (tf + BM25_K))
        if score <= 0:
            continue
        scored.append((score, Match(
            folder=ep["folder"],
            title=ep.get("title", ep["folder"]),
            snippet=ep.get("description", "")[:200],
            source="structured",
            links=ep.get("links", {}),
        )))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored]


# --- Source 2: Transcript search ---
# Scans every transcript.{md,txt} file for matching terms.
# For each matching line, grabs a 7-line context window (3 before, 3 after)
# and scores it by IDF-weighted term hits. Keeps only the best block per episode.
def transcript(terms: list[str], episode_filter: str | None = None) -> list[Match]:
    pattern = re.compile("|".join(morpho(t) for t in terms), re.IGNORECASE)
    term_pats = [(re.compile(morpho(t), re.IGNORECASE), idf(t)) for t in terms]
    best: dict[str, list[tuple[float, int, int, str, int]]] = {}  # folder -> [(score, start, end, block, line)]
    for tf in sorted(REPO_ROOT.glob("*/transcript.*")):
        if tf.suffix not in (".md", ".txt"):
            continue
        folder = tf.parent.name
        if episode_filter and folder != episode_filter:
            continue
        try:
            lines = tf.read_text(errors="ignore").splitlines()
        except OSError:
            continue
        total_lines = len(lines)
        for i, line in enumerate(lines):
            if not pattern.search(line):
                continue
            start = max(0, i - 3)
            end = min(total_lines, i + 4)
            block = "\n".join(lines[start:end])
            score = 0
            for tp, w in term_pats:
                tf_count = len(tp.findall(block))
                if tf_count > 0:
                    score += w * (tf_count / (tf_count + BM25_K))
            # Length normalization: penalize very long transcripts
            norm = 1.0 / (1 + total_lines / 5000)
            score *= (0.5 + 0.5 * norm)
            if score <= 0:
                continue
            blocks = best.setdefault(folder, [])
            blocks.append((score, start, end, block, i + 1))
            # Keep only top-N blocks per episode (sort by score descending)
            if len(blocks) > BLOCKS_PER_EPISODE * 2:
                blocks.sort(key=lambda b: b[0], reverse=True)
                best[folder] = blocks[:BLOCKS_PER_EPISODE * 2]

    results = []
    for folder, blocks in best.items():
        blocks.sort(key=lambda b: b[0], reverse=True)
        top = blocks[:BLOCKS_PER_EPISODE]
        merged = merge_blocks(top)
        # Pick the highest-scoring merged block
        merged.sort(key=lambda b: b[0], reverse=True)
        winner = merged[0]
        score, start, end, block_text, line = winner
        # Re-read block text for merged ranges
        for tf in REPO_ROOT.glob(f"{folder}/transcript.*"):
            if tf.suffix in (".md", ".txt"):
                try:
                    all_lines = tf.read_text(errors="ignore").splitlines()
                    block_text = "\n".join(all_lines[start:end])
                    filepath = str(tf.relative_to(REPO_ROOT))
                except OSError:
                    filepath = f"{folder}/transcript.md"
                break
        else:
            filepath = f"{folder}/transcript.md"
        results.append((score, Match(
            folder=folder,
            title=folder,
            snippet=block_text,
            source="transcript",
            line=line,
            file=filepath,
            timestamp=extract_timestamp(block_text),
        )))
    results.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in results]


# --- Source 3: Code search ---
# Walks episode directories looking for code files, grep-matches terms,
# scores by IDF, and keeps the best matching line per episode.
CODE_EXTENSIONS = {".py", ".ts", ".tsx", ".baml"}

# Folder name date prefix to strip before extracting topic words
FOLDER_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")
EXCLUDED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__",
                 ".mypy_cache", "bm25_index", "oracle", ".github"}

def code(terms: list[str], episode_filter: str | None = None) -> list[Match]:
    pattern = re.compile("|".join(morpho(t) for t in terms), re.IGNORECASE)
    term_pats = [(re.compile(morpho(t), re.IGNORECASE), idf(t)) for t in terms]
    best: dict[str, tuple[float, Match]] = {}
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT, topdown=True):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for fname in filenames:
            if Path(fname).suffix not in CODE_EXTENSIONS:
                continue
            cf = Path(dirpath) / fname
            folder = cf.relative_to(REPO_ROOT).parts[0]
            if not EPISODE_DIR_RE.match(folder):
                continue
            if episode_filter and folder != episode_filter:
                continue
            try:
                lines = cf.read_text(errors="ignore").splitlines()
            except OSError:
                continue
            for i, line in enumerate(lines):
                if not pattern.search(line):
                    continue
                score = 0
                for tp, w in term_pats:
                    tf = len(tp.findall(line))
                    if tf > 0:
                        score += w * (tf / (tf + BM25_K))
                prev = best.get(folder, (0, None))[0]
                if score > prev:
                    best[folder] = (score, Match(
                        folder=folder,
                        title=folder,
                        snippet=line.strip(),
                        source="code",
                        line=i + 1,
                        file=str(cf.relative_to(REPO_ROOT)),
                    ))
    return [m for _, m in sorted(best.values(), key=lambda x: x[0], reverse=True)]


# --- Source 4: Topics from folder names ---
# Parses episode folder names like "2025-06-17-entity-extraction" into topic words
# ["entity", "extraction"] and scores against query terms. Provides a cheap 4th
# signal for RRF — agreement across more sources strengthens relevance.
def topics(terms: list[str], episodes: list[dict] | None = None) -> list[Match]:
    if episodes is None:
        episodes = load_episodes()
    patterns = [(re.compile(morpho(t), re.IGNORECASE), idf(t)) for t in terms]
    scored = []
    for ep in episodes:
        slug = FOLDER_DATE_RE.sub("", ep["folder"])
        words = slug.replace("-", " ")
        score = 0
        for pat, w in patterns:
            tf = len(pat.findall(words))
            if tf > 0:
                score += w * (tf / (tf + BM25_K))
        if score <= 0:
            continue
        scored.append((score, Match(
            folder=ep["folder"],
            title=ep.get("title", ep["folder"]),
            snippet=slug.replace("-", " "),
            source="topics",
            links=ep.get("links", {}),
        )))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored]




# Reciprocal Rank Fusion: merge multiple ranked lists into one.
#
# For each episode appearing at rank r in a source list, add 1/(k+r+1) to its score.
# Episodes found by multiple sources accumulate higher scores — this is the key insight
# of RRF: agreement between independent sources is a strong relevance signal.
#
# After scoring, two gates filter noise:
#   Gate 1: drop episodes scoring below 30% of the top result (or below absolute floor)
#   Gate 2: prefer episodes found by 2+ sources; hard cap at 8 results
def rrf(ranked_lists: list[list[Match]], episodes: list[dict] | None = None, k: int = RRF_K) -> FusionResult:
    scores: dict[str, float] = {}
    best: dict[str, Match] = {}
    source_count: dict[str, set[str]] = {}
    timestamps: dict[str, int] = {}

    for ranked in ranked_lists:
        seen = set()
        for rank, match in enumerate(ranked):
            folder = match.folder
            if folder in seen:
                continue
            seen.add(folder)
            # Core RRF formula: 1/(k + rank + 1)
            scores[folder] = scores.get(folder, 0) + 1 / (k + rank + 1)
            source_count.setdefault(folder, set()).add(match.source)
            if match.timestamp is not None and folder not in timestamps:
                timestamps[folder] = match.timestamp
            # Prefer transcript matches for display (they have timestamps + quotes)
            if folder not in best or (match.source == "transcript" and best[folder].source != "transcript"):
                best[folder] = match

    # Enrich matches with metadata from data.json
    if episodes is None:
        episodes = load_episodes()
    ep_map = {ep["folder"]: ep for ep in episodes}
    sorted_folders = sorted(scores, key=lambda f: scores[f], reverse=True)

    matches = []
    for folder in sorted_folders:
        m = best[folder]
        ep = ep_map.get(folder, {})
        m.title = ep.get("title", folder)
        m.links = ep.get("links", {})
        m.source_count = len(source_count.get(folder, set()))
        if m.timestamp is None and folder in timestamps:
            m.timestamp = timestamps[folder]
        matches.append(m)

    # Gate 1: drop weak results (relative to top score + absolute minimum)
    if matches:
        top = scores[matches[0].folder]
        matches = [m for m in matches if scores[m.folder] >= top * RRF_SCORE_FLOOR
                   and (scores[m.folder] >= RRF_MIN_SCORE or m.source_count >= 3)]

    # Gate 2: if 2+ episodes have multi-source agreement, only show those (up to 8).
    # Otherwise show top 3 from whatever we have.
    multi = [m for m in matches if m.source_count >= 2]
    if len(multi) >= 2:
        matches = multi[:8]
    else:
        matches = matches[:3]

    return FusionResult(matches=matches, scores=scores)


# Lightweight reranker applied after RRF fusion.
# Rescores the top results using signals not captured by the individual sources:
#   - Title-query overlap: boost episodes whose title words match query terms
#   - Recency bias: slightly prefer newer episodes for ambiguous queries
#   - Description density: count how many query terms appear in the description
# Weights are additive on top of the existing RRF score.
RERANK_TITLE_W = 0.15
RERANK_RECENCY_W = 0.05
RERANK_DESC_W = 0.10

def rerank(result: FusionResult, terms: list[str], episodes: list[dict] | None = None) -> FusionResult:
    if not result.matches or not terms:
        return result
    if episodes is None:
        episodes = load_episodes()
    ep_map = {ep["folder"]: ep for ep in episodes}
    # Sort all folders by date to compute recency rank
    all_folders = sorted(ep_map.keys(), reverse=True)
    recency_rank = {f: i for i, f in enumerate(all_folders)}
    total = max(len(all_folders), 1)
    lower_terms = [t.lower() for t in terms]
    term_pats = [re.compile(morpho(t), re.IGNORECASE) for t in terms]

    scores = dict(result.scores)
    for m in result.matches:
        ep = ep_map.get(m.folder, {})
        # Title overlap: fraction of query terms found in title
        title = ep.get("title", "").lower()
        title_hits = sum(1 for p in term_pats if p.search(title))
        scores[m.folder] += RERANK_TITLE_W * (title_hits / len(terms))
        # Recency: linear decay from 1.0 (newest) to 0.0 (oldest)
        rank = recency_rank.get(m.folder, total)
        scores[m.folder] += RERANK_RECENCY_W * (1 - rank / total)
        # Description density: fraction of query terms in description
        desc = ep.get("description", "").lower()
        desc_hits = sum(1 for p in term_pats if p.search(desc))
        scores[m.folder] += RERANK_DESC_W * (desc_hits / len(terms))

    reranked = sorted(result.matches, key=lambda m: scores[m.folder], reverse=True)
    return FusionResult(matches=reranked, scores=scores)


# Run all 4 sources in sequence and fuse results.
# query_type is passed through but currently unused — all sources run regardless.
# episode_filter restricts transcript/code search to a single episode folder.
def search(
    terms: list[str],
    query_type: str,
    episode_filter: str | None = None,
) -> FusionResult:
    if not terms:
        return FusionResult(matches=[], scores={})
    episodes = load_episodes()
    sources = [
        structured(terms, episodes),
        transcript(terms, episode_filter),
        code(terms, episode_filter),
        topics(terms, episodes),
    ]
    result = rrf([s for s in sources if s], episodes)
    return rerank(result, terms, episodes)
