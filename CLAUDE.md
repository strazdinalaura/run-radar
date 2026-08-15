# Run Radar

You're helping Laura with her race radar — an automated pipeline that finds and judges running races daily.

## Quick start

`/radar` — Run the pipeline and show new races.

## How it works

GitHub Actions runs `main.py` daily at 6am: fetch races → check Supabase → judge with Claude Haiku → save. Open `dashboard.html` to review.

## Rules

- **prefs.md is the source of truth.** Judge tuning goes in `config/prefs.md`, not hardcoded in code.
- **After prefs changes**, run `python eval.py` — score must stay ≥76%.
- **Never commit secrets.** Keys live in `.env` (local) and GitHub Secrets (cloud).
- **Never `git add .`** — stage files by name.
