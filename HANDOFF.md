# HANDOFF — Run Radar

> CLAUDE.md recreated 2026-07-12 — it now holds the goal, phase map, and rules. This file holds only current state. On conflict, CLAUDE.md wins.

## Current phase

**Phase 3 — Judge: ✅ COMPLETE (2026-07-12).** Real judge (`USE_STUB = False`, `claude-haiku-4-5-20251001`) scored 22/29 (76%), beating the 72% stub baseline. Remaining 7 misses are borderline maybe/no calls — accepted, not tuning further (overfit risk). Note: Anthropic API calls only work on Laura's machine; Cowork's sandbox proxy blocks them (plain-text 401 that looks like a bad key — it isn't).

## Phase map (reconstructed)

1. Fetch (fetch.py) — ✅ done. RunSignup API, SF 50mi radius, 180-day horizon.
2. Snapshot/diff (db.py) — ✅ done. SQLite insert-if-absent, events = first_seen today. 103 races in seen.db.
3. Judge (judge.py) — ✅ done. Real API, 76% vs labels, beats stub baseline.
4. Runner/digest — ✅ done. Real-API test passed 2026-07-12 (10 unseen races re-judged, digest written). URL-prefix bug fixed same day.
5. Supabase / cloud — not started. Laura opened account creation 2026-07-12; deferred until Phase 4 ships.

## Last session (2026-07-12)

**Phase 4 real-API test: ✅ PASSED**
- `unsee.py 10` deleted 10 races; `main.py` re-detected all 10 as new
- 10 Haiku API calls completed successfully
- Judge results: 1 maybe (Run for Mental Health SF), 9 no
- Digest printed to terminal ✅
- digest.md updated with dated entry ✅
- Minor bug noted: URL has duplicate `https://runsignup.com` prefix (cosmetic, not blocking)

## Next step

**Phase 5 — Supabase (fresh session).** Roadmap agreed 2026-07-12: 5) Supabase swap, 6) GitHub repo + Actions cron, 7) web page (deploy via Vercel, reads Supabase Data API directly). Laura preps before the session: finish Supabase project creation (save the DB password somewhere safe), then Settings → API → copy Project URL + anon key + service_role key into .env. Table creation happens in-session: we write the SQL, she pastes it into Supabase's SQL Editor.

## Decisions

- 2026-07-12: Supabase (Phase 5) requested, gated. Order: fix judge → build Phase 4 runner → then Supabase. Rationale: no point syncing unjudged data to the cloud.
- 2026-07-12: Judge fix lives in prefs.md, not the judge prompt. Rationale: one source of truth; prompt few-shot rejected as overfit-prone. Laura rejected Claude Code's judge.py prompt edit for the same reason.
- 2026-07-12: API key confirmed working (Claude Code ran 29 real calls). Earlier 401s were Cowork sandbox proxy, not the key.
- 2026-07-12: Phase 3 closed at 76%; remaining 7 misses accepted as borderline. Fresh eval labels needed before any future judge tuning (current labels are now "training data").
- 2026-07-12: Digest format = terminal print + append to digest.md (newest entry first). Rationale: history of what surfaced, useful once runs are scheduled.
- 2026-07-12: Phase 4 test method = unsee.py (delete N rows, re-detect as new) instead of expanding fetch to all California. Rationale: CA expansion = destination-races v2 flag in disguise, and prefs reject most of it anyway.
- Supabase workflow when we get there: no GitHub connection needed; `supabase` pip package; mirror seen.db schema; swap db.py internals only.

- 2026-07-12: Early Phase 6 exception approved by Laura: git init + push to PRIVATE GitHub repo now (protects state files; HANDOFF vanished once). Actions cron still waits for Phase 5 (Supabase) — a cloud run can't use laptop SQLite.
- 2026-07-12: HANDOFF.md + CLAUDE.md get committed. Rationale: backup + history in a private repo outweighs public-scrub risk; repo stays private, friends only ever see the Vercel page.

## v2 flags

- Destination races (separate fetch scope) — from prefs.md
- GitHub Actions cron for scheduled runs (only relevant post-Phase 5)
