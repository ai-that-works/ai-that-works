---
name: oracle
description: Search the AI That Works podcast archive. Finds episodes by topic, transcript quotes, code symbols, or vague descriptions. Use when someone asks which episode covered a topic, where a code pattern appeared, or for a specific quote from the show.
argument-hint: <query>
allowed-tools:
  - Bash
  - Read
---

# Oracle

Search the AI That Works podcast archive and synthesize an answer from what the hosts (Dex and Vaibhav) actually said.

## Step 1: Retrieve

Run the oracle search in JSON mode to get structured results:

```bash
cd oracle && python3 oracle.py --json "$ARGUMENTS"
```

## Step 2: Read transcript context

For each result that has a `transcript` field and a `line` number, read ~50 lines of context around the match using the Read tool:

- Use the `transcript` path (relative to the repo root) as the file
- Read from `line - 25` to `line + 25` (clamped to file bounds)
- Read up to 3 transcripts max (the top-ranked results)

For results without a line number but with a transcript file, read lines 1-150 to get the episode intro context.

## Step 3: Synthesize

Using the transcript excerpts you just read, write a response that **cites inline like an academic paper**, not in a references dump at the end.

### Citation style

- Attribute claims to hosts and link the source **right where you make the claim**, e.g.:

  > Vaibhav argued that evals are "the single most important thing you can ship before your product" ([Ep 31 — Evals Deep Dive](https://youtube.com/watch?v=xxx&t=412)).

  > Dex pushed back, noting that "if your eval suite takes 40 minutes nobody's gonna run it" ([Ep 31 — Evals Deep Dive](https://youtube.com/watch?v=xxx&t=587)).

- For YouTube links, append `?t=TIMESTAMP` (or `&t=TIMESTAMP` if the URL already has params) when a timestamp is available.
- Use the episode title as the link text, prefixed with the episode number if known.
- Direct quotes from hosts go in quotation marks. Paraphrased ideas don't need quotes but still get an inline citation.
- Do NOT collect references into a list at the end. Every claim gets its source right there in the text.

### Other rules

- If the results are episode lookups (by number/date) rather than topic searches, just present the episode info with description and links — no need to read transcripts.
- Do NOT dump the raw oracle output. Read what was said and give the user a synthesized answer grounded in the actual conversation.
