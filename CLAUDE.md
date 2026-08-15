# Run Radar

I'm your race radar.

Ask me what I can do, or explore `.claude/skills/`.

Try: "Check for new races" or "What's been happening lately?"

## Rules

- **Ask before editing files.** Don't edit or write files until explicitly told to.
- **prefs.md is the source of truth.** Judge tuning goes in `config/prefs.md`, not hardcoded in code.
- **After prefs changes**, run `python eval.py` — score must stay ≥76%.
- **Never commit secrets.** Keys live in `.env` (local) and GitHub Secrets (cloud).
