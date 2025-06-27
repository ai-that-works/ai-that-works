# Automated Video Summarization & Draft Distribution – **V0 Specification**

> **Focus**: Build the thinnest slice that turns a Zoom cloud recording into (1) an unlisted YouTube video and (2) three AI‑generated text drafts (email, X, LinkedIn) that a human can review and edit inside a single web UI. **No auto‑publishing, scheduling, or advanced analytics in V0.**

---

## 1 Scope

| In‑scope (V0 MVP)                                                                 | Out‑of‑scope (deferred)                |
| --------------------------------------------------------------------------------- | -------------------------------------- |
| • OAuth connections for Zoom & Google (YouTube)                                   | X / LinkedIn OAuth & direct publishing |
| • Download Zoom recording to backend                                              | Rich WYSIWYG editor, comment threads   |
| • Upload video to YouTube as *Unlisted*                                           | Metrics, analytics, dashboards         |
| • Send video URL to Gemini 2.5 Pro → get \`\`                                     | Auto‑transcription outside Gemini      |
| • Generate email / X / LinkedIn copy via prompt template                          | Prompt designer UI, multiple templates |
| • Persist artefacts & status in Supabase                                          | Job retries UI, observability stack    |
| • Next.js UI: list videos, display draft text fields, allow inline edits & "Save" | “Approve & publish”, scheduling flows  |

---

## 2 Architecture Snapshot (V0)

```
Zoom  ──► FastAPI backend ──► YouTube (unlisted)
                   │
                   └─► Gemini 2.5 Pro ──► summary_points
                                     │
Supabase  ◀────────┴─ store video & drafts
    ▲
    │  realtime
Next.js UI  ◀──────────────────────────────
```

* **Backend** (Python 3.12 + FastAPI) handles Zoom → YouTube → Gemini pipeline.
* **Database**: Supabase Postgres; tables: `videos`, `drafts`.
* **Frontend** (Next.js 14, TypeScript) subscribes to Supabase to live‑refresh UI.

---

## 3 Data Model (updated for summary + feedback)

```sql
-- videos (one row per recording)
CREATE TYPE video_status AS ENUM ('new','downloaded','uploaded','summarised','error');
CREATE TABLE videos (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  zoom_meeting_id text NOT NULL,
  youtube_video_id text,
  transcript jsonb NOT NULL,
  status video_status DEFAULT 'new',
  title text,
  created_at timestamptz DEFAULT now(),
  points jsonb,          -- ordered bullet points (null if not summarised)
);

-- drafts (versioned per channel)
CREATE TYPE draft_channel AS ENUM ('email','x','linkedin');
CREATE TABLE drafts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id uuid REFERENCES videos(id) ON DELETE CASCADE,
  channel draft_channel NOT NULL,
  version int NOT NULL DEFAULT 1, -- 1 = first AI generation
  content text NOT NULL,
  generated bool DEFAULT true,    -- false once edited by human
  created_at timestamptz DEFAULT now()
);
CREATE UNIQUE INDEX drafts_unique_channel_version ON drafts(video_id, channel, version);

-- feedback on individual draft versions
CREATE TABLE feedback (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  draft_id uuid REFERENCES drafts(id) ON DELETE CASCADE,
  user_id uuid REFERENCES auth.users(id),
  body text NOT NULL,
  created_at timestamptz DEFAULT now()
);
```

---

## 4 Key API Endpoints (Backend → Frontend)

| Method                                 | Path                                                                                                  | Purpose |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------- |
| `POST /videos/import`                  | Body: `{zoom_meeting_id}` → queues download job; returns `{video_id}`                                 |         |
| `GET  /videos/{id}`                    | Returns Video DTO incl. latest summary & current drafts                                               |         |
| `POST /videos/{id}/summarize`          | Triggers Gemini pipeline; creates `summary` row + first‑gen drafts                                    |         |
| `GET  /videos/{id}/summary`            | Returns persisted `summary_points` JSON                                                               |         |
| `GET  /videos/{id}/drafts?channel={c}` | List draft history (ordered by `version`)                                                             |         |
| `POST /video/{id}/drafts`              | Body: `{content}`  + `{channel}` →  adds new content with next version number, sets `generated=false` |         |
| `POST /drafts/{id}/feedback`           | Body: `{body}` → create feedback row + create a new draft (version++)                                 |         |
|                                        |                                                                                                       |         |

All DTOs generated via **pydantic** and served through FastAPI’s OpenAPI schema.

---

## 5 UI Flow (Next.js)

1. **Dashboard** – table of recordings (status badges).
2. **Detail Page** – left: embedded YouTube player; right: three textarea fields pre‑filled with AI drafts.

   1. **Save** button persists updates to `drafts` table via RPC.
   2. Feedback section

*(No approval/publish buttons in V0)*

---

## 6 Non‑Functional Targets

DO NOT DO ANY OF THESE ACTION YET UNLESS SPECIFICALLY TOLD TO.

* **Throughput**: one recording processed at a time; queue depth ≤10 acceptable.
* **Latency**: ≤10 min from import to drafts (network & Gemini latency bound).
* **Security**: Supabase RLS — users can only see their own rows. Secrets in env vars.
* **CI**: lint + unit tests; deploy backend to Fly.io, frontend to Vercel.

---

---

## Stack Guidelines

- Frontend - ONLY USE NPX and NPM. Use React and nextjs, use shadcn ONLY for ui components, biomejs for linting
- Python - ONLY USE UV and UVX - not pip, not pipx, not poetry
- AI - Use BAML


