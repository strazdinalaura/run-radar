# Run Radar

Run Radar finds running races for you automatically. It:
1. Pulls races from RunSignup (SF area, 50-mile radius, next 180 days)
2. Remembers what it's already seen (so you only see new races)
3. Judges each race against your preferences using Claude Haiku
4. Surfaces only the good ones (yes/maybe) in a digest

## Use it

```
python3 main.py
```

Then read `digest.md`. That's the whole routine.

## What happens when it runs

```
1. FETCH      all races near SF, next 180 days, from RunSignup
2. COMPARE    which of these have I not seen before?
3. JUDGE      new races only → Claude reads prefs.md → yes / maybe / no
4. DIGEST     yes + maybe go to digest.md, with a reason each
```

A race is judged once, the first time it appears, then remembered forever.
Most runs end with "nothing new" — that's the radar working, not failing.

## My files vs machinery

Mine — I read or edit these:

- `digest.md` — the output. Races worth a look, newest on top.
- `prefs.md` — my taste, written in plain English. The judge obeys this
  file. If judgments feel off, the fix is here — not in code.

Machinery — scripts manage these, I don't touch them:

- `main.py` (the button), `fetch.py`, `db.py`, `judge.py`, `seen.db` (the memory)

Tools — for checking on the machinery:

- `eval.py` — grades the judge against `eval_labels.md`, 30 races I labeled
  by hand. Run after any prefs.md change.
- `unsee.py` — makes N old races look new again, to watch the pipeline work.

## Fixing things

**Judge rejected a race I'd want, or promoted junk.**
Edit prefs.md — say the preference plainly, like explaining to a friend.
Then `python3 eval.py` to confirm the score didn't drop.

**I want to see it judge something right now.**
`python3 unsee.py 10 && python3 main.py` — re-judges 10 old races. Costs cents.

**Claude in Cowork claims my API key is broken (401).**
It isn't — Cowork's sandbox can't reach the Anthropic API. Anything calling
Claude (main.py, eval.py) runs on my laptop: Terminal or Claude Code.
