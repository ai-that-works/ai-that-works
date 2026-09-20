# luma_to_loops

Adds Luma calendar contacts to a Loops mailing list, one way, additively.

## What it does (and does not do)

For each email address on the Luma calendar:

- **Already in Loops** → skipped entirely. No name update, no list change, no
  subscription change. The existing contact is never written to.
- **Not in Loops** → created with the email, plus first/last name if Luma has
  them, subscribed to the mailing list(s) you pass.

Duplicates within Luma itself (the same person across multiple events) are
collapsed to one entry before anything is sent.

Nothing is written unless you pass `--apply`.

## Setup

Requires `LUMA_API_KEY` (needs a Luma Plus subscription) and `LOOPS_API_KEY` in
the repo root `.env`. Both are already set.

## Usage

Run from `2026-02-17-automating-aitw/`:

```bash
# Find the mailing list ID
uv run python -m src.luma_to_loops.sync --list-mailing-lists

# Dry run: see how many are new without writing anything
uv run python -m src.luma_to_loops.sync --list-id <LIST_ID>

# Try it against the first 25 Luma contacts only
uv run python -m src.luma_to_loops.sync --list-id <LIST_ID> --max-contacts 25

# Do it, and save a report
uv run python -m src.luma_to_loops.sync \
  --list-id <LIST_ID> \
  --apply \
  --output /absolute/path/to/luma_to_loops.json
```

`--list-id` is repeatable if you want new contacts on more than one list.
`--source` sets the origin label shown in Loops (default: `Luma`).

## Interrupted runs

A full run is a few thousand Loops lookups, so every answer is checkpointed to
`.luma_to_loops_cache.jsonl` as it comes back. If the run dies partway — dropped
connection, Ctrl-C, closed laptop — just run the same command again and it picks
up where it left off instead of re-querying from the top. Pass `--cache PATH` to
put the checkpoint somewhere else, or `--no-cache` to disable it.

Successful creations are written to the cache too, so a re-run after a partial
`--apply` will not try to create them again.

Delete the cache file when you want a genuinely fresh check (for example, if
you've since added people to Loops by hand).

## Notes

- Loops allows 10 requests/sec per team; the client throttles to 8 and retries
  429s, 5xxs, read timeouts and dropped connections with exponential backoff.
  The run costs 1 lookup per unique Luma email, plus 1 create per new contact,
  so expect roughly `unique_emails / 8` seconds.
- An address that still fails after its retries is recorded under
  `lookup_failed` and the run continues; the process exits non-zero so a failure
  is not mistaken for a clean run.
- `subscribed` is never sent. Anyone who previously unsubscribed in Loops stays
  that way, and existing contacts keep their state because they are never
  touched.
- The JSON report lists every address by bucket (`already_in_loops`, `to_add`,
  `created`, `failed`), so a failed run can be reviewed before re-running. Re-runs
  are safe: anything created the first time is found in Loops and skipped.

## APIs used

- Luma: `GET /v1/calendars/contacts/list` (cursor paginated)
- Loops: `GET /v1/lists`, `GET /v1/contacts/find`, `POST /v1/contacts/create`
