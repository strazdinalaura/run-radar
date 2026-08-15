# Run Radar Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   GITHUB    │     │  SUPABASE   │     │   BROWSER   │
│   Actions   │     │  Database   │     │  dashboard  │
│             │     │             │     │             │
│ Runs daily  │────▶│ races table │◀────│ Reads data  │
│ at 6am PT   │     │ judgments   │     │ shows digest│
│             │     │ bucket_list │     │             │
│ main.py     │     │ feedback    │     │ Local HTML  │
└─────────────┘     └─────────────┘     └─────────────┘
      │                                        │
      ▼                                        ▼
  Anthropic API                          Only Laura
  (judge races)                          (not hosted)

Trigger: Automatic (6am cron) or manual `python main.py`
Output:  Supabase tables + digest.md + dashboard.html
```
