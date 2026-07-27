# HANDOFF — Run Radar

> CLAUDE.md recreated 2026-07-12 — it now holds the goal, phase map, and rules. This file holds only current state. On conflict, CLAUDE.md wins.

## Current phase

**Phase 8 — Local Dashboard: 🟡 IN PROGRESS.** Mockup designed in Claude Design. Next: enable RLS, wire HTML to Supabase.

## Phase map (revised 2026-07-25)

| Phase | What | Status |
|-------|------|--------|
| 1 | Fetch (fetch.py) — RunSignup API, SF 50mi, 180 days | ✅ done |
| 2 | Memory (db.py) — SQLite diff, first_seen tracking | ✅ done |
| 3 | Judge (judge.py) — Real API, 76% accuracy | ✅ done |
| 4 | Runner (main.py) — fetch→diff→judge→digest | ✅ done |
| 5 | Supabase — swap SQLite→cloud, judgments stored | ✅ done |
| 6 | GitHub Actions — cron runs daily, no laptop needed | ✅ done |
| 7 | Attendance tracking — mark races, calendar export, review flow | ✅ done |
| 8 | Local dashboard — HTML that reads Supabase, browser-only, NOT public | 🟡 in progress |
| 9 | Public deploy — Vercel, auth, environments (FUTURE, not scheduled) | deferred |

## Last session (2026-07-25)

**Phase 7 — Attendance Tracking: ✅ COMPLETE**
- Added `attending` boolean column to races table
- Added `logo_url` text column to races table
- Updated fetch.py to capture logo_url from RunSignUp API
- Updated db.py with new functions: mark_attending(), get_attending_races(), get_upcoming_races(), get_new_races_with_judgments()
- Created attend.py CLI:
  - `python attend.py review` — see new races with judgments (YES/MAYBE/NO)
  - `python attend.py list` — see upcoming races
  - `python attend.py add <race_id>` — mark as attending
  - `python attend.py remove <race_id>` — unmark
  - `python attend.py calendar` — generate races.ics
- Added 2 manual races (not from RunSignUp): Alexi Pappas 10K (Jul 26), Golden Gate 10K (Aug 2)
- Generated races.ics — imported to Google Calendar successfully
- Created backfill_images.py — smart backfill (only surfaced/attending races, not all 140)
- Backfilled 4 races with real logo_url from RunSignUp

**Phase 8 — Local Dashboard: 🟡 STARTED**
- Designed mockup in Claude Design (connected to GitHub repo)
- Layout: "Surfaced for you" (recommendations) → "Your races" (attending) → "Radar activity" (stats)
- Real race images via logo_url working
- Exported HTML ready to wire up
- **Tabled for now:** RLS setup, Supabase connection, JavaScript wiring

**Discussed but deferred:**
- Running journal / workout tracking (weekly workout schedule)
- Google Calendar MCP (Laura will connect herself)
- Strava integration

## Session (2026-07-24)

**Phase 6 GitHub Actions: ✅ COMPLETE**
- Manual run verified successful
- Added `schedule` trigger to daily.yml (cron: 6am Pacific / 13:00 UTC)
- Radar now runs automatically every day, no laptop needed

## Session (2026-07-19)

**Phase 5 Supabase: ✅ COMPLETE**
- Created Supabase project: `https://wfomjzjydjikloclcgtd.supabase.co`
- Created tables: `races` (108 rows), `judgments` (5 rows)
- Migrated 106 races from seen.db via `migrate.py`
- Rewrote `db.py` to use Supabase instead of SQLite
- Updated `main.py` to save judgments to Supabase
- Test run successful: 5 new races judged, all saved to Supabase
- Learned Supabase security: GRANTs for tables + sequences, RLS enabled

**Folder reorganization:**
```
run-radar/
├── config/           ← prefs.md, eval_labels.md
├── docs/             ← CLAUDE.md, HANDOFF.md, ARCHITECTURE.md
├── to_delete/        ← seen.db, migrate.py, unsee.py (obsolete)
├── main.py, fetch.py, db.py, judge.py, eval.py
├── digest.md, README.md, requirements.txt, .env
```
- Updated `judge.py` and `eval.py` paths for new structure
- Updated `eval.py` to use Supabase instead of SQLite
- Updated `README.md` with new structure

**Phase 6 GitHub Actions: 🟡 STARTED**
- Created `.github/workflows/daily.yml` (manual trigger, schedule commented out)
- Added 3 secrets to GitHub: `ANTHROPIC_API_KEY_RUN_RADAR`, `SUPABASE_URL_RUN_RADAR`, `SUPABASE_SERVICE_ROLE_KEY_RUN_RADAR`
- Added credentials map to `docs/ARCHITECTURE.md`
- Test run queued but GitHub runners were slow (known GitHub issue, not our code)
- **Next:** Re-run workflow to verify it works, then enable schedule

## Next step

**Phase 8 — Bucket List + Dashboard (when ready).**

### 8a. Bucket List table
1. Create `bucket_list` table in Supabase (SQL below)
2. Add `source` column to `races` table
3. Seed with initial races (SF Marathon, Golden Gate 10K, etc.)

```sql
-- Bucket list table
CREATE TABLE bucket_list (
  id serial PRIMARY KEY,
  name text NOT NULL,
  location text,
  typical_month text,
  url text,
  notes text,
  logo_url text,
  created_at date DEFAULT CURRENT_DATE
);

-- Add source column to races
ALTER TABLE races ADD COLUMN source text DEFAULT 'runsignup';

-- Grant permissions
GRANT ALL ON bucket_list TO service_role;
GRANT USAGE, SELECT ON SEQUENCE bucket_list_id_seq TO service_role;
```

### 8b. Wire up dashboard
1. Enable RLS on all tables
2. Add read/update policies for anon key
3. Export HTML from Claude Design, save to run-radar/
4. Add Supabase credentials + JavaScript to make it live

**Dashboard sections:**
1. Surfaced for you (RunSignUp + judgments)
2. Bucket list (curated flagship races)
3. Your races (attending=true)
4. Radar activity (stats)

**Exit criteria:** Open dashboard.html in browser, see all sections with real data, click "I'M IN" on bucket list race and it creates an attending entry.

## Decisions

- 2026-07-25: **Bucket list feature.** New `bucket_list` table for curated flagship races (SF Marathon, Golden Gate 10K, destination races). Solves the problem that RunSignUp only covers ~30% of races. Bucket list is manual, skips judge, one-click "I'M IN" creates attending entry in races table.
- 2026-07-25: **Smart backfill.** Only backfill logo_url for races that appear on dashboard (surfaced + attending), not all 140. Saves API calls and tokens.
- 2026-07-25: **Dashboard hierarchy.** "Surfaced for you" (recommendations) at top — this is the smart part. "Your races" (attending) second. Stats at bottom.
- 2026-07-25: **Dashboard stays local.** HTML file on laptop, not hosted. Only Laura sees it. RLS protects data even if anon key exposed.
- 2026-07-25: **Manual races supported.** Races not in RunSignUp (Alexi Pappas 10K, Golden Gate 10K) can be added manually with negative race_id.
- 2026-07-19: **Folder reorganization.** Created `docs/`, `config/`, `to_delete/` folders. Docs (CLAUDE.md, HANDOFF.md, ARCHITECTURE.md) moved to docs/. Config (prefs.md, eval_labels.md) moved to config/. Obsolete files (seen.db, migrate.py, unsee.py) moved to to_delete/ for Laura to delete manually. Python scripts stay at root to avoid import changes.
- 2026-07-19: **Supabase security setup.** Learned that new Supabase projects use "revoke by default" — must explicitly GRANT table + sequence permissions to service_role. RLS enabled on both tables; no policies yet (service_role bypasses RLS anyway). Policies will be added in Phase 7 for anon key access.
- 2026-07-19: **CLAUDE.md rule 10 updated** with Supabase API key vocabulary: secret key (service_role) = backend only; publishable key (anon) = frontend OK with RLS.
- 2026-07-18: **Roadmap revised.** Original Phase 7 (public Vercel) split into: Phase 7 (local viewer, no deploy), Phase 8 (chat.py agent, local only), Phase 9 (public deploy, deferred). Rationale: Laura wants to build a working local agent first, learn the stack, then go public when ready. No TypeScript/frameworks — Python + raw HTML + SQL only.
- 2026-07-18: Chat agent confirmed as goal. Phase 8 will use **Supabase MCP** instead of chat.py — Laura chats with Claude Code directly, Claude queries Supabase via MCP. Simpler than writing a custom script. Guardrail: Anthropic console spending cap before Phase 6 cron ships.
- 2026-07-12: Supabase (Phase 5) requested, gated. Order: fix judge → build Phase 4 runner → then Supabase. Rationale: no point syncing unjudged data to the cloud.
- 2026-07-12: Judge fix lives in prefs.md, not the judge prompt. Rationale: one source of truth; prompt few-shot rejected as overfit-prone. Laura rejected Claude Code's judge.py prompt edit for the same reason.
- 2026-07-12: API key confirmed working (Claude Code ran 29 real calls). Earlier 401s were Cowork sandbox proxy, not the key.
- 2026-07-12: Phase 3 closed at 76%; remaining 7 misses accepted as borderline. Fresh eval labels needed before any future judge tuning (current labels are now "training data").
- 2026-07-12: Digest format = terminal print + append to digest.md (newest entry first). Rationale: history of what surfaced, useful once runs are scheduled.
- 2026-07-12: Phase 4 test method = unsee.py (delete N rows, re-detect as new) instead of expanding fetch to all California. Rationale: CA expansion = destination-races v2 flag in disguise, and prefs reject most of it anyway.
- Supabase workflow when we get there: no GitHub connection needed; `supabase` pip package; mirror seen.db schema; swap db.py internals only.

- 2026-07-12: Early Phase 6 exception approved by Laura: git init + push to PRIVATE GitHub repo now (protects state files; HANDOFF vanished once). Actions cron still waits for Phase 5 (Supabase) — a cloud run can't use laptop SQLite.
- 2026-07-12: HANDOFF.md + CLAUDE.md get committed. Rationale: backup + history in a private repo outweighs public-scrub risk; repo stays private, friends only ever see the Vercel page.

- 2026-07-12: CLAUDE.md rules 9 (git guardrails) + 10 (security duty: block secret leaks, service_role in frontend, RLS-less Data API, accidental publicity, unbounded spend) added at Laura's request.
- 2026-07-12: Git initialized on Laura's machine via Claude Code; first commit made; gh CLI installed + device-flow auth.
- 2026-07-12: **GitHub repo CONFIRMED** — https://github.com/strazdinalaura/run-radar | Private: ✅ | .env in repo: ❌ (safe) | seen.db in repo: ❌ (safe)
- 2026-07-12: Laura advised to rotate API key (old one passed through a chat transcript) and set an Anthropic console spending cap before Actions cron ships.

## v2 flags

- **Running journal** — track weekly workouts (Monday: easy 5mi, Tuesday: speed work, etc.)
- **Strava integration** — pull actual workout data
- **Geographic visualization** — map view of races (local + bucket list destinations)
- **Google Calendar MCP** — Claude creates calendar events directly
- **Registration alerts** — check bucket list URLs for "registration open" signals
- **Multi-source fetch** — scrape BayAreaRaces.com or add Active.com API
