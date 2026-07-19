# HANDOFF — Run Radar

> CLAUDE.md recreated 2026-07-12 — it now holds the goal, phase map, and rules. This file holds only current state. On conflict, CLAUDE.md wins.

## Current phase

**Phase 5 — Supabase: ✅ COMPLETE (2026-07-19).** SQLite swapped for Supabase. `main.py` now writes races + judgments to cloud. 108 races, 5 judgments in Supabase.

## Phase map (revised 2026-07-19)

| Phase | What | Status |
|-------|------|--------|
| 1 | Fetch (fetch.py) — RunSignup API, SF 50mi, 180 days | ✅ done |
| 2 | Memory (db.py) — SQLite diff, first_seen tracking | ✅ done |
| 3 | Judge (judge.py) — Real API, 76% accuracy | ✅ done |
| 4 | Runner (main.py) — fetch→diff→judge→digest | ✅ done |
| 5 | Supabase — swap SQLite→cloud, judgments stored | ✅ done |
| 6 | **GitHub Actions** — cron runs daily, no laptop needed | **next** |
| 7 | Local viewer — HTML that reads Supabase, browser-only, NOT public | after 6 |
| 8 | Chat agent — Supabase MCP so Claude Code can query races directly | after 7 |
| 9 | Public deploy — Vercel, auth, environments (FUTURE, not scheduled) | deferred |

**Key change from original plan:** Phase 7 is now local-only viewer (no Vercel). Phase 8 adds chat agent. Public deployment deferred to Phase 9 until Laura is ready to learn environments/auth.

## Last session (2026-07-19)

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

## Next step

**Phase 6 — GitHub Actions.**
- Push updated code to GitHub repo
- Create `.github/workflows/daily.yml` cron job
- Add Supabase + Anthropic keys to GitHub Secrets
- Test: scheduled run succeeds without laptop
- Exit criteria: Supabase gets new races daily via cloud cron

## Decisions

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

- Destination races (separate fetch scope) — from prefs.md
- GitHub Actions cron for scheduled runs (only relevant post-Phase 5)
