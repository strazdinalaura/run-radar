# Run Radar

A personal race-finding tool that scans for running races, judges them against my preferences, and helps me decide what to run.

## What it does

```
Every morning at 6am:
  1. Fetches races near SF (50mi radius, next 180 days)
  2. Judges new ones: YES / MAYBE / NO
  3. Saves everything to Supabase

When I open the dashboard:
  - See new recommendations
  - Swipe yes/no (feedback improves the judge)
  - Track races I'm attending
  - Browse my bucket list
```

## Quick start

```bash
# Run manually
python main.py

# Check new races with judgments
python attend.py review

# Mark a race as attending
python attend.py add <race_id>
```

Or just open `dashboard.html` in a browser.

## How it's organized

```
run-radar/
├── main.py              ← Daily radar (fetch → judge → save)
├── attend.py            ← Mark races, review recommendations
├── dashboard.html       ← Visual interface (coming soon)
│
├── config/
│   └── prefs.md         ← My preferences (edit to tune the judge)
│
├── docs/
│   ├── DATA_FLOW.txt    ← How data moves through the system
│   ├── SECURITY.txt     ← Keys and permissions
│   └── DESIGN.txt       ← Dashboard design principles
│
└── digest.md            ← Text log of surfaced races
```

## Data lives in Supabase

| Table | Purpose |
|-------|---------|
| `races` | All discovered races |
| `judgments` | AI recommendations (yes/maybe/no) |
| `bucket_list` | Flagship races I care about |
| `feedback` | My responses (trains the judge) |

## Fixing the judge

If the judge gets it wrong, edit `config/prefs.md` in plain English.
Then run `python eval.py` to check accuracy didn't drop.
