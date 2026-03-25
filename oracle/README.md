# Oracle

Search engine for the [AI That Works](https://github.com/ai-that-works/ai-that-works) podcast archive. Oracle is a [Claude Code skill](https://docs.anthropic.com/en/docs/claude-code/skills) backed by a Python retrieval script. Type `/oracle` followed by a query and Claude searches the transcript archive, reads the matched sections, and writes a synthesized answer with inline citations linking to YouTube timestamps.

The idea came from Vaibhav and Dex making a request during [Episode 48: Claude Agent Skills Deep Dive](https://www.youtube.com/watch?v=b5O6gb_Zuk8) where they asked for this kind of system, so I decided to try and build it.

The Python script (`oracle.py`) handles indexing and retrieval. It can be used standalone from the terminal, but its primary purpose is powering the Claude Code skill.

## Claude Code skill

Type `/oracle` followed by a query:

```
/oracle which episodes cover evals?
```

The skill runs `oracle.py --json` behind the scenes, reads ~50 lines of transcript context around each match, then responds with something like:

> Vaibhav argued that evals are "the single most important thing you can ship before your product" ([Designing Evals](https://youtu.be/-N6MajRfqYw?t=412)). Dex pushed back, noting that "if your eval suite takes 40 minutes nobody's gonna run it" ([Multimodal Evals](https://www.youtube.com/watch?v=jzhVo0iAX_I&t=3396)).

Every claim links directly to the YouTube timestamp where it was said. No list of search results — just an answer grounded in the actual conversation.

## GitHub Actions workflow

A GitHub Actions workflow (`.github/workflows/oracle-index.yml`) automatically rebuilds the search index when episode content changes. It triggers on pushes to `main` that modify:
- `*/transcript.*` (episode transcripts)
- `*/data.json` or `data.json` (episode metadata)
- `oracle/index.py` or `oracle/fusion.py` (indexer code)

The rebuilt `docfreq.json` and `symbols.json` are committed back by the bot. No manual reindexing needed — push a transcript and the index updates itself.

## CLI

You can also use Oracle directly from the terminal.

Build the index (run once, or after adding episodes):

```
python3 oracle/index.py
```

Query:

```
python3 oracle/oracle.py "which episodes cover evals?"
```

JSON output (used by the Claude Code skill):

```
python3 oracle/oracle.py --json "memory systems"
```

## Explanation of System

Oracle's pipeline has three stages: **classify**, **retrieve + fuse**, and **rerank**.

### 1. Classify

`oracle.py` parses the query into one of five intents:

| Intent | Example | Behavior |
|---|---|---|
| EpisodeLookup | "episode 12", "#42" | Direct lookup by number or date in `data.json` |
| LatestEpisode | "latest episode" | Sort episodes by date, return newest |
| CodeSymbol | "ContextWindow" | Validates against `symbols.json`, splits camelCase for broader matching |
| TranscriptSearch | "what did they say about evals" | Full transcript grep with context windows |
| VagueTopic | "which episodes cover traces?" | Runs all four retrieval sources |

Before searching, Oracle strips function words ("the", "is", "for"), intent words ("episode", "podcast", "cover"), and terms with IDF below 0.5 (words appearing in nearly every episode).

### 2. Retrieve + Fuse

Four independent retrieval sources run against the query terms, each scored with BM25 term-frequency saturation and IDF weighting:

| Source | What it searches | How it scores |
|---|---|---|
| **Structured** | Episode titles and descriptions from `data.json` | IDF-weighted morphological regex match |
| **Transcript** | `transcript.md` / `transcript.txt` files with 7-line context windows | IDF-weighted hits with length normalization, merges nearby blocks |
| **Code** | `.py`, `.ts`, `.tsx`, `.baml` files in episode directories | Best matching line per episode, IDF-weighted |
| **Topics** | Folder name slugs (e.g. `2025-06-17-entity-extraction` → "entity extraction") | IDF-weighted word overlap against query terms |

Results are merged using [Reciprocal Rank Fusion](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) (Cormack et al., 2009). For each episode at rank *r* in source list *i*, RRF adds `1/(60 + r + 1)` to the episode's score. Episodes found by multiple sources accumulate higher scores.

Two gates filter noise after fusion:
- **Relative floor**: drop anything below 30% of the top score
- **Multi-source preference**: if 2+ episodes have multi-source agreement, only show those (up to 8)

### 3. Rerank

A lightweight reranker rescores the fused results using three signals not captured by the individual sources:
- **Title overlap** — boost episodes whose title words match query terms
- **Recency** — slightly prefer newer episodes for ambiguous queries
- **Description density** — count how many query terms appear in the description

### Morphological matching

Oracle expands search terms into regex patterns that capture inflected forms. "eval" matches `eval`, `evals`, `evaluate`, `evaluation`. "classify" matches `classify`, `classification`, `classifier`. This happens at query time.
