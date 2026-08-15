# Run Radar Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   GITHUB    │     │  SUPABASE   │     │    AGENT    │
│   Actions   │     │  Database   │     │             │
│             │     │             │     │  /radar     │
│ Runs daily  │────▶│ races table │◀────│  /recap     │
│ at 6am PT   │     │ judgments   │     │             │
│             │     │ bucket_list │     │  Claude +   │
│ main.py     │     │             │     │  MCP        │
└─────────────┘     └─────────────┘     └─────────────┘
      │                                        │
      ▼                                        ▼
  Anthropic API                          Conversational
  (judge races)                          (runs when you ask)

Trigger: Automatic (6am cron) or manual `python main.py`
Output:  Supabase tables
```
