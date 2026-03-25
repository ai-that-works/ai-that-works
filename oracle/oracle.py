import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import fusion
from fusion import CODE_EXTENSIONS, CODE_STRUCTURAL

# Oracle: local search engine for the "AI That Works" podcast archive.
#
# Given a natural language query (e.g. "which episode covered evals?"),
# oracle finds matching episodes by searching transcripts, metadata, and code.
#
# Pipeline:
#   1. classify_heuristic() — parse query intent (episode lookup, latest, date, topic)
#      and extract search terms with stopword removal, IDF filtering, synonym expansion
#   2. fusion.search() — run 4-source retrieval (structured, transcript, code, topics),
#      merge via Reciprocal Rank Fusion, then rerank with title/recency/description signals
#   3. render() — format results for display
#
# No API key needed. When used as a Claude Code skill, the host LLM handles
# classification and formatting inline — this file is the CLI entrypoint.

# Closed-class English words stripped from queries before searching.
# Domain-specific low-value terms are filtered separately by IDF_FLOOR.
FUNCTION_WORDS = {
    "a", "an", "the",
    "i", "me", "my", "we", "our", "you", "your", "he", "she", "it", "they", "them",
    "is", "are", "was", "were", "am", "be", "been", "do", "does", "did",
    "in", "on", "at", "to", "for", "of", "from", "with", "by",
    "and", "or", "but", "if", "that", "which", "who", "what", "how",
    "this", "some", "any", "all", "ever", "can", "about",
}

# Words describing the medium itself ("episode", "podcast") — not the content.
# Stripped so "which episodes talk about evals" searches for just "evals".
INTENT_STOPS = {"episode", "episodes", "podcast", "show",
                "talk", "talks", "talked", "discuss", "cover", "covered"}

# Terms appearing in almost every episode have low IDF and add noise.
# Anything below this threshold is dropped from the search terms.
IDF_FLOOR = 0.5


# --- Query classification regexes ---
# Match "episode 12", "ep 5", "#42"
EPISODE_RE = re.compile(r"(?<!\w)(?:episodes?|eps?|#)\s*(\d+)\b", re.IGNORECASE)
# Match trailing numbers after commas/and: "episodes 3, 7 and 12" -> captures 7, 12
BARE_NUM_RE = re.compile(r"(?:,\s*|(?:and|&)\s+)(\d+)\b", re.IGNORECASE)
# Match "latest", "newest", "most recent", "last"
LATEST_RE = re.compile(r"\b(?:latest|newest|most\s+recent|last)\b", re.IGNORECASE)
# Match ISO dates like 2025-06-17
DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")


# Cached set of known code identifiers from the repo (built by index.py).
# Used to validate whether a camelCase/snake_case token is a real symbol.
_symbols_cache = None

def load_symbols() -> set[str]:
    global _symbols_cache
    if _symbols_cache is not None:
        return _symbols_cache
    path = Path(__file__).resolve().parent / "symbols.json"
    if not path.exists():
        _symbols_cache = set()
        return _symbols_cache
    _symbols_cache = set(json.loads(path.read_text()))
    return _symbols_cache


# Split "ContextWindow" -> ["Context", "Window"] for broader matching.
def split_camel(s: str) -> list[str]:
    return re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', s)


# Output of query classification. type is one of:
#   EpisodeLookup  — user asked for a specific episode by number or date
#   LatestEpisode  — user wants the most recent episode(s)
#   CodeSymbol     — query contains a known code identifier
#   TranscriptSearch — user wants a specific quote or timestamp
#   VagueTopic     — general topic search (most common)
@dataclass
class HeuristicParsed:
    type: str
    search_terms: list[str]
    wants_code: bool
    episode_numbers: list[int] = None
    date_prefix: str | None = None

    def __post_init__(self):
        if self.episode_numbers is None:
            self.episode_numbers = []


# Classify a raw query string into a structured intent.
# Priority: episode numbers > "latest" > date > code symbols > transcript keywords > vague topic.
def classify_heuristic(raw: str) -> HeuristicParsed:
    # --- Priority 1: explicit episode number ("episode 12", "ep 5", "#42") ---
    ep_matches = EPISODE_RE.findall(raw)
    if ep_matches:
        numbers = [int(n) for n in ep_matches]
        # Also grab trailing bare numbers: "episodes 3, 7 and 12" -> 7, 12
        bare = BARE_NUM_RE.findall(raw)
        numbers.extend(int(n) for n in bare if int(n) not in numbers)
        return HeuristicParsed(type="EpisodeLookup", search_terms=[str(n) for n in numbers], wants_code=False, episode_numbers=numbers)

    # --- Priority 2: "latest" / "newest" / "most recent" ---
    if LATEST_RE.search(raw):
        return HeuristicParsed(type="LatestEpisode", search_terms=[], wants_code=False)

    # --- Priority 3: ISO date like 2025-06-17 ---
    date_match = DATE_RE.search(raw)
    if date_match:
        return HeuristicParsed(type="EpisodeLookup", search_terms=[date_match.group(1)], wants_code=False, date_prefix=date_match.group(1))

    # --- Priority 4: topic search (most queries land here) ---
    # Strip stopwords and low-IDF terms to get meaningful search terms
    words = raw.split()
    stops = FUNCTION_WORDS | INTENT_STOPS
    terms = [w.strip("?.,!\"'") for w in words if w.strip("?.,!\"'").lower() not in stops]
    terms = [t for t in terms if len(t) > 1 and fusion.idf(t) >= IDF_FLOOR]

    # Detect code-like tokens (camelCase, snake_case) and transcript-related keywords
    has_code_token = any(CODE_STRUCTURAL.search(t) for t in terms)
    wants_code = any(w in raw.lower() for w in ["code", "pull", "show me the code", "source"])

    if has_code_token and not any(w in raw.lower() for w in ["episode", "talk", "cover"]):
        # Query looks like a code symbol search
        qtype = "CodeSymbol"
        code_tokens = [t for t in terms if CODE_STRUCTURAL.search(t)]
        symbols = load_symbols()
        # If the token is a known symbol, also search its camelCase parts
        # e.g. "ContextWindow" adds "Context" and "Window" as extra terms
        extras = []
        for tok in code_tokens:
            if tok not in symbols:
                continue
            parts = split_camel(tok)
            if len(parts) > 1:
                extras.extend(parts)
        if extras:
            terms = terms + extras
        elif not any(tok in symbols for tok in code_tokens):
            # Looks code-like but isn't a known symbol — fall back to topic search
            qtype = "VagueTopic"
    elif any(w in raw.lower() for w in ["quote", "said", "transcript", "minute", "timestamp"]):
        qtype = "TranscriptSearch"
    else:
        qtype = "VagueTopic"

    return HeuristicParsed(
        type=qtype,
        search_terms=terms[:12],  # cap to avoid overly broad searches
        wants_code=wants_code,
    )


# --- Snippet extraction ---
# When showing transcript results, we want to pick the most informative line
# from a matched block, skipping filler ("yeah um okay") and intro boilerplate.

# Strip inline timestamps like "(12:34)" from transcript text
TIMESTAMP_STRIP_RE = re.compile(r"^.*?\(\d{1,2}:\d{2}(?:\.\d+)?\)\s*\n?", re.MULTILINE)

# Common conversational filler — lines dominated by these words are skipped.
FILLER_WORDS = {"good", "okay", "right", "sure", "yeah", "yes", "no", "yep",
                "nope", "uh", "um", "ah", "oh", "hm", "hmm", "huh", "wow",
                "exactly", "correct", "absolutely", "totally", "interesting",
                "cool", "nice", "great", "awesome", "thanks",
                "i", "mean", "like", "just", "you", "know", "so", "well",
                "thing", "that", "the", "is", "it", "a", "an", "in", "and",
                "but", "or", "we", "they", "he", "she", "do", "not", "be",
                "have", "had", "was", "were", "are", "been", "has"}

# True if >60% of words are filler or the line is too short to be useful.
def filler_heavy(line: str) -> bool:
    words = re.findall(r"\w+", line.lower())
    if len(words) < 3:
        return True
    return sum(1 for w in words if w in FILLER_WORDS) / len(words) > 0.6

# Skip podcast intro boilerplate when selecting snippets
INTRO_RE = re.compile(
    r"(?:welcome|hey everyone|hello|what's up|good morning|good afternoon|"
    r"today we|this is|i'm your host|my name is|co-host|let's get started|"
    r"thanks for (?:joining|tuning|listening|watching))",
    re.IGNORECASE,
)


# Pick the best single line from a transcript block to show the user.
# Prefers lines that mention the search terms, skipping filler and intros.
def pick_snippet(block: str, terms: list[str]) -> str:
    clean = TIMESTAMP_STRIP_RE.sub("", block).strip()
    lines = [l.strip() for l in clean.split("\n") if l.strip()]
    candidates = [l for l in lines if not filler_heavy(l) and len(l) >= 20 and not INTRO_RE.search(l)]
    if not candidates:
        candidates = [l for l in lines if len(l) >= 20]
    if not candidates:
        candidates = lines
    if not candidates:
        return clean[:120]
    if not terms:
        return candidates[0][:120]
    lower_terms = [t.lower() for t in terms]
    best = max(candidates, key=lambda l: sum(1 for t in lower_terms if t in l.lower()))
    return best[:120]


# Format a FusionResult into human-readable text output.
# Shows episode title, source count, best snippet, code files (if requested), and links.
def render(result: fusion.FusionResult, wants_code: bool = False, terms: list[str] | None = None) -> str:
    if not result.matches:
        return "No episodes matched."

    n = len(result.matches)
    lines = [f"{n} {'episode' if n == 1 else 'episodes'} matched:", ""]
    for i, m in enumerate(result.matches, 1):
        lines.append(f"{i}. {m.title} ({m.folder}) [{m.source_count} source{'s' if m.source_count != 1 else ''}]")
        if m.source == "transcript" and m.timestamp is not None:
            best = pick_snippet(m.snippet, terms or [])
            lines.append(f"   transcript at {fusion.format_timestamp(m.timestamp)}: {best}")
        elif m.file and m.line:
            lines.append(f"   {m.file}:{m.line}: {m.snippet[:120]}")
        elif m.snippet:
            lines.append(f"   {m.snippet[:200]}")
        if wants_code:
            ep_dir = fusion.REPO_ROOT / m.folder
            if ep_dir.is_dir():
                code_files = sorted(
                    p.relative_to(fusion.REPO_ROOT)
                    for p in ep_dir.rglob("*")
                    if p.is_file() and p.suffix in CODE_EXTENSIONS
                )
                for cf in code_files[:5]:
                    lines.append(f"   {cf}")
                if len(code_files) > 5:
                    lines.append(f"   ... and {len(code_files) - 5} more files")
        yt = m.links.get("youtube")
        if yt and m.timestamp is not None:
            sep = "&" if "?" in yt else "?"
            lines.append(f"   {yt}{sep}t={m.timestamp}")
        elif yt:
            lines.append(f"   {yt}")
        for key, url in m.links.items():
            if key == "youtube":
                continue
            lines.append(f"   {url}")
        lines.append("")
    return "\n".join(lines)


# Extract episode number from guid like "aitw-042" -> 42.
# Fallback lookup when episode["episode"] field is missing.
def guid_number(ep: dict) -> int | None:
    g = ep.get("guid", "")
    if g.startswith("aitw-"):
        try:
            return int(g.split("-")[1])
        except (IndexError, ValueError):
            return None
    return None


# Main entry point. Takes a raw query string, classifies it, retrieves results,
# and returns formatted text. Handles all query types:
#   - Episode number lookup (direct match against data.json)
#   - Latest episode (sort by date)
#   - Date prefix lookup (match folder names like "2025-06-17-*")
#   - Topic/code/transcript search (delegates to fusion.search + RRF)
def query_json(raw: str) -> list[dict]:
    parsed = classify_heuristic(raw)
    matches = []

    if parsed.episode_numbers:
        episodes = fusion.load_episodes()
        for num in parsed.episode_numbers:
            found = [ep for ep in episodes if ep.get("episode") == num]
            if not found:
                found = [ep for ep in episodes if guid_number(ep) == num]
            for ep in found:
                matches.append(fusion.Match(
                    folder=ep["folder"],
                    title=ep.get("title", ep["folder"]),
                    snippet=ep.get("description", "")[:200],
                    source="structured",
                    links=ep.get("links", {}),
                    source_count=1,
                ))
    elif parsed.type == "LatestEpisode":
        episodes = fusion.load_episodes()
        by_date = sorted(episodes, key=lambda e: e["folder"], reverse=True)
        for ep in by_date[:3]:
            matches.append(fusion.Match(
                folder=ep["folder"],
                title=ep.get("title", ep["folder"]),
                snippet=ep.get("description", "")[:200],
                source="structured",
                links=ep.get("links", {}),
                source_count=1,
            ))
    elif parsed.date_prefix is not None:
        episodes = fusion.load_episodes()
        for ep in episodes:
            if ep["folder"].startswith(parsed.date_prefix):
                matches.append(fusion.Match(
                    folder=ep["folder"],
                    title=ep.get("title", ep["folder"]),
                    snippet=ep.get("description", "")[:200],
                    source="structured",
                    links=ep.get("links", {}),
                    source_count=1,
                ))
                break
    elif parsed.search_terms:
        result = fusion.search(terms=parsed.search_terms, query_type=parsed.type)
        matches = result.matches

    out = []
    for m in matches:
        entry = {
            "folder": m.folder,
            "title": m.title,
            "snippet": m.snippet,
            "source": m.source,
            "links": m.links,
            "source_count": m.source_count,
        }
        if m.file:
            entry["file"] = m.file
        if m.line:
            entry["line"] = m.line
        if m.timestamp is not None:
            entry["timestamp"] = m.timestamp
        # find transcript file for this episode
        ep_dir = fusion.REPO_ROOT / m.folder
        for ext in ("md", "txt"):
            tf = ep_dir / f"transcript.{ext}"
            if tf.exists():
                entry["transcript"] = str(tf.relative_to(fusion.REPO_ROOT))
                break
        out.append(entry)
    return out


def query(raw: str) -> str:
    parsed = classify_heuristic(raw)

    # Direct episode number lookup — bypass search entirely
    if parsed.episode_numbers:
        episodes = fusion.load_episodes()
        matches = []
        for num in parsed.episode_numbers:
            found = [ep for ep in episodes if ep.get("episode") == num]
            if not found:
                found = [ep for ep in episodes if guid_number(ep) == num]
            for ep in found:
                matches.append(fusion.Match(
                    folder=ep["folder"],
                    title=ep.get("title", ep["folder"]),
                    snippet=ep.get("description", "")[:200],
                    source="structured",
                    links=ep.get("links", {}),
                    source_count=1,
                ))
        if matches:
            scores = {m.folder: 1.0 for m in matches}
            return render(fusion.FusionResult(matches=matches, scores=scores))
        return "No episodes matched."

    if parsed.type == "LatestEpisode":
        episodes = fusion.load_episodes()
        by_date = sorted(episodes, key=lambda e: e["folder"], reverse=True)
        matches = []
        for ep in by_date[:3]:
            matches.append(fusion.Match(
                folder=ep["folder"],
                title=ep.get("title", ep["folder"]),
                snippet=ep.get("description", "")[:200],
                source="structured",
                links=ep.get("links", {}),
                source_count=1,
            ))
        scores = {m.folder: 1.0 - i * 0.1 for i, m in enumerate(matches)}
        return render(fusion.FusionResult(matches=matches, scores=scores))

    if parsed.date_prefix is not None:
        episodes = fusion.load_episodes()
        for ep in episodes:
            if ep["folder"].startswith(parsed.date_prefix):
                m = fusion.Match(
                    folder=ep["folder"],
                    title=ep.get("title", ep["folder"]),
                    snippet=ep.get("description", "")[:200],
                    source="structured",
                    links=ep.get("links", {}),
                    source_count=1,
                )
                return render(fusion.FusionResult(matches=[m], scores={ep["folder"]: 1.0}))
        return "No episodes matched."

    if not parsed.search_terms:
        return "No episodes matched."

    result = fusion.search(terms=parsed.search_terms, query_type=parsed.type)
    return render(result, wants_code=parsed.wants_code, terms=parsed.search_terms)


def main():
    if len(sys.argv) < 2:
        print("Usage: oracle '<query>'")
        print("Tip: quote your query to prevent shell expansion")
        sys.exit(1)
    args = sys.argv[1:]
    if args[0] == "--json":
        print(json.dumps(query_json(" ".join(args[1:])), indent=2))
        return
    print(query(" ".join(args)))


if __name__ == "__main__":
    main()
