---
description: Give feedback on races to update preferences
---

# /feedback

## Start

Read `config/prefs.md` and show a quick summary of current preferences.

Then explain:

"Here's how to give feedback:

- **Attending a race:** 'I'm attending [race name]'
- **Disagree with judgment:** '[race] should be yes/no/maybe'
- **New preference:** 'I like [thing]' or 'I don't like [thing]'

Give me your feedback, then say **done** when finished.
I'll update your preferences in one batch and run eval to check the score."

## Collect

Listen for feedback. Note:
- Races the user is attending (mark in Supabase)
- Mismatches between user opinion and judgment
- New preferences to add

Don't edit prefs.md yet.

## Finish

When user says "done" (or "finished", "that's all"):

1. Summarize: "Here's what I heard: [list feedback]"
2. Show what will be added to prefs.md (if any)
3. Ask: "OK to update?"
4. If confirmed: ONE edit to prefs.md
5. Eval runs automatically via hook
6. Report: "Score: X% → Y%"

If no preference changes needed (just attending updates), skip the prefs edit.
