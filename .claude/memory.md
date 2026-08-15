# Memory

## Current state
- **Phase 8 (Local Dashboard)**: In progress. HTML wired to Supabase, needs anon key.
- **Phase 9 (Public Deploy)**: Deferred. Vercel + auth when ready.
- Dashboard file: `dashboard.html` — open in browser to review races.

## Key decisions

### Architecture
- **2026-07-18**: Chat via Claude Code + Supabase MCP, not a custom `chat.py` script. Simpler.
- **2026-07-19**: Supabase replaces SQLite. `service_role` key for backend, `anon` for frontend with RLS.
- **2026-07-19**: Python scripts stay at root (no import changes). Docs in `docs/`, config in `config/`.

### Data model
- **2026-07-25**: `bucket_list` table for flagship races (SF Marathon, Big Sur, etc). RunSignUp only covers ~30% of interesting races.
- **2026-07-25**: Manual races supported with negative `race_id`. Used for Alexi Pappas 10K, Golden Gate 10K.
- **2026-07-25**: `source` column added to `races` table to distinguish RunSignUp vs manual.

### Dashboard
- **2026-07-25**: Dashboard stays local (HTML file on laptop, not hosted). Only Laura sees it.
- **2026-07-25**: Hierarchy: "Surfaced for you" (top) → "Bucket list" → "Your races" → "Stats" (bottom).
- **2026-07-25**: Hero card pattern (Tinder-style) for feedback loop. One race at a time, yes/pass.

### Judge
- **2026-07-12**: Judge logic lives in `config/prefs.md`, not hardcoded in `judge.py` prompts.
- **2026-07-12**: Eval baseline is 76%. Any prefs change must maintain this score.
- **2026-07-12**: Current eval labels are now "training data" — need fresh labels before major tuning.

### Security
- **2026-07-19**: RLS enabled on all tables before anon key goes in dashboard.
- **2026-07-12**: Spending cap on Anthropic console recommended before heavy cron usage.
- **2026-07-12**: Repo is private. Audit git history for secrets before any public switch.

## Context
- Laura's first race: Golden Gate 10K, August 2, 2026
- Interested in: Lafayette Reservoir trail races, Big Sur 11-Miler (April 2027)
- Big Sur logistics: Free race shuttles from Monterey, no car needed

## v2 ideas (not started)
- Race logistics planner (transportation, hotels)
- Running journal (weekly workouts)
- Strava integration
- Google Calendar MCP for event creation
- Registration alerts for bucket list races
