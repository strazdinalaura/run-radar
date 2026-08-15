# Memory

## Current state
- Pipeline runs daily at 6am via GitHub Actions
- Agent layer with skills on top
- Supabase stores races + judgments

## Key decisions

### Architecture
- **Scripts vs skills:** Scripts for automation/scheduling/testing. Skills for interaction/queries.
- **2026-07-18**: Chat via Claude Code + Supabase MCP, not a custom script.
- **2026-07-19**: Supabase replaces SQLite. `service_role` key for backend.

### Data model
- **2026-07-25**: `bucket_list` table for flagship races. RunSignUp only covers ~30% of interesting races.
- **2026-07-25**: Manual races supported with negative `race_id`.

### Judge
- **2026-07-12**: Judge logic lives in `config/prefs.md`, not hardcoded.
- **2026-07-12**: Eval baseline is 76%. Any prefs change must maintain this score.

### Security
- **2026-07-19**: RLS enabled on all tables.
- **2026-07-12**: Repo is private. Audit git history for secrets before any public switch.

## Context
- Laura's first race: Golden Gate 10K, August 2, 2026
- Interested in: Lafayette Reservoir trail races, Big Sur 11-Miler (April 2027)

## v2 ideas
- Race logistics planner
- Strava integration
- Google Calendar MCP
