---
description: Show recent radar activity or upcoming races
---

# /recap

Ask the user what they want to see:

**Looking back (radar activity):**
- Races added in the last 7, 14, or 30 days
- Query `races` table by `first_seen`
- Show judgments (yes/maybe/no) for each

**Looking forward (upcoming races):**
- Races happening this week, this month, or next 30 days
- Query `races` table by `date`
- Highlight any marked as attending

Use Supabase MCP to query. Summarize what you find.
