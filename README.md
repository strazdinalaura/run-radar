# Run Radar

This project helps me discover races I wouldn't find otherwise.
It's tuned for the Bay Area — 50 miles around SF, 6 months out.
Every morning at 6am, the pipeline runs. Most mornings, so do I.
An AI judge decides if a race fits me — it's read my preferences, so it knows I hate turkey trots.
When I disagree with a call, I tell it — and it learns.
When I want to know what's new, there's an agent that catches me up.

## How it works

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│   6am daily                                                    │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌───────────┐  │
│   │ RunSign │───▶│  Judge  │───▶│  Save   │───▶│ Supabase  │  │
│   │ Up API  │    │ (Haiku) │    │         │    │           │  │
│   └─────────┘    └─────────┘    └─────────┘    └───────────┘  │
│                                                       │        │
│   Pipeline: fetch → judge → save                      │        │
│                                                       ▼        │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│   When I ask                                                   │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  Agent (Claude + MCP)                                   │  │
│   │  /radar    — run the pipeline                          │  │
│   │  /recap    — what's new, what's coming up              │  │
│   │  /feedback — I tell it what I think, it learns         │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Explore

**Want to see how the Bay Area tuning works?**
→ Check `fetch.py` — pulls from RunSignUp API, filtered by zipcode, radius, time horizon

**Want to see how races get judged?**
→ Check `judge.py` and `config/prefs.md` — my preferences in plain English

**Want to see how the agent works?**
→ Check `.claude/skills/` — `/radar`, `/recap`, and `/feedback`

## Stack

`python` · `claude haiku` · `supabase` · `github actions` · `claude code`

---

*Built for discovering races so I can focus on running them.*
