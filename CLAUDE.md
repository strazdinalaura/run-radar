# CLAUDE.md — Run Radar spec & rules

This file is the spec and the leash. Any Claude (Cowork or Claude Code)
working in this folder reads this first, then HANDOFF.md for current state.
On conflict, this file wins.

## The goal (definition of done)

The project is COMPLETE when all three are true:

1. **Supabase** — race memory + judgments live in a Supabase (free tier)
   database instead of local seen.db
2. **GitHub** — code lives in a GitHub repo, and a GitHub Actions cron runs
   the radar daily without Laura's laptop
3. **Vercel** — "Laura's Race Radar" web page is live on a Vercel (free Hobby
   tier) URL, readable on her phone, shareable with friends

Hard constraint: **$0 hosting.** Free tiers only — Supabase free, GitHub free,
Vercel Hobby. If any step would require a paid plan, stop and ask Laura.
The only running cost is the Anthropic API (cents per run) — that's accepted.

## Phase map

| Phase | What | Exit criteria | Status |
|-------|------|--------------|--------|
| 1 | Fetch (fetch.py) | Pulls SF-area races from RunSignup | ✅ done |
| 2 | Memory (db.py) | Diff: only never-seen races surface | ✅ done |
| 3 | Judge (judge.py) | Real API beats stub baseline on eval labels | ✅ done (76% > 72%) |
| 4 | Runner (main.py) | fetch → diff → judge → digest, real-API tested | ✅ done |
| 5 | Supabase | main.py run writes to Supabase; judgments stored too; seen.db retired | next |
| 6 | GitHub + Actions | Repo pushed; cron runs daily ~6am; a scheduled run succeeds with no laptop | after 5 |
| 7 | Web page | Vercel URL shows current yes/maybe races from Supabase Data API; works on phone | after 6 |

## Rules (both Claudes)

1. **Session ritual**: read HANDOFF.md before working, update it before
   stopping. Recap phase + next step to Laura at session start.
2. **Phase gate**: one phase per session. Work belonging to a later phase is
   either logged as a flag or needs Laura's explicit override. "Quickly add X"
   gets the same check.
3. **README.md is Laura's.** Never overwrite, restructure, or "improve" it.
   Edits only when she explicitly asks, and only the lines she asks about.
4. **prefs.md is the judge's only source of truth.** Judge fixes go there,
   in plain English — never hardcoded into judge.py prompts or rules.
5. **Secrets**: .env never gets committed (it's gitignored — keep it that way).
   In GitHub Actions, keys live in repo Secrets. The service_role key never
   appears in web page code.
6. **After any prefs.md change**, run eval.py; score must stay ≥ 76%.
   If eval labels get stale (they're now training data), flag for fresh labels.
7. **Design decisions** go to Laura as 2 options max, one-line tradeoff each.
   Decided → logged in HANDOFF.md Decisions.
8. **Boring code wins.** The radar is snapshot → diff → surface. No
   abstractions for imagined futures.

## Who does what

- **Laura**: runs anything that needs her accounts (Terminal/Claude Code runs,
  Supabase dashboard clicks, GitHub/Vercel signup), makes design decisions,
  owns prefs.md and README.md.
- **Cowork Claude**: architecture, code writing, HANDOFF upkeep, session
  protocol. Cannot call the Anthropic API from its sandbox (401 = sandbox,
  not the key).
- **Claude Code**: runs and tests things on Laura's machine. Follows the
  instruction block Laura pastes; doesn't edit judge logic, prefs, or README
  unless the instruction says so.
