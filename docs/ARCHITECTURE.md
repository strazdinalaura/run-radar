# Run Radar Architecture

## Current State

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

## When Things Run

```
PYTHON (daily at 6am, or manual)         JAVASCRIPT (when you open dashboard)
────────────────────────────────         ────────────────────────────────────

Finds races                              Shows races
Judges them          ───►  SUPABASE  ───►   to you
Stores results              (data)          Handles clicks
                                            Saves feedback

Python fills the database. JavaScript shows it to you.
```

| What | When | How often |
|------|------|-----------|
| Python (fetch + judge) | 6am via GitHub Actions | Daily |
| JavaScript | When you open dashboard.html | On demand |
| Supabase | Always on | 24/7 |

## Future State (Vercel — Phase 9, deferred)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   GITHUB    │     │  SUPABASE   │     │   VERCEL    │
│   Actions   │     │  Database   │     │   Web Page  │
│             │     │             │     │             │
│ Runs daily  │────▶│ races table │◀────│ Reads data  │
│ at 6am      │     │ judgments   │     │ shows digest│
│             │     │             │     │             │
│ main.py     │     │             │     │ Phone-      │
│             │     │             │     │ friendly    │
└─────────────┘     └─────────────┘     └─────────────┘
      │                                        │
      ▼                                        ▼
  Anthropic API                          Shareable URL
  (judge races)                          (public)

Not implemented yet. Current dashboard is local HTML only.
```

## Service Responsibilities

| Service | What it does | Cost |
|---------|--------------|------|
| **GitHub** | Stores code, runs scheduled jobs | Free |
| **Supabase** | Stores races + judgments (replaces seen.db) | Free tier |
| **Vercel** | Hosts web page | Free tier |
| **Anthropic** | Claude Haiku judges races | ~$0.01/run |

## Data Flow

```
1. FETCH     RunSignup API → raw race data
2. DIFF      Compare against Supabase → only new races continue
3. JUDGE     New races → Claude Haiku → yes/maybe/no
4. STORE     Write to Supabase (races + judgments)
5. DISPLAY   Web page reads from Supabase → shows yes/maybe
```

## Credentials Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                      CREDENTIALS MAP                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ANTHROPIC_API_KEY (sk-ant-...)                                     │
│  ├── Local: .env                    ← your laptop runs main.py     │
│  └── Cloud: GitHub Secrets          ← Actions runs main.py         │
│                                                                     │
│  SUPABASE_URL (https://xxx.supabase.co)                             │
│  ├── Local: .env                                                    │
│  └── Cloud: GitHub Secrets                                          │
│                                                                     │
│  SUPABASE_SERVICE_ROLE_KEY (eyJ... secret)                          │
│  ├── Local: .env                                                    │
│  └── Cloud: GitHub Secrets                                          │
│  └── NEVER: frontend code, git history, logs                        │
│                                                                     │
│  SUPABASE_PUBLISHABLE_KEY (eyJ... public)                           │
│  ├── Local: .env (optional)                                         │
│  └── Future: Vercel env vars (Phase 9)                              │
│  └── OK in: frontend code (with RLS enabled)                        │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  WHERE EACH SERVICE GETS CREDENTIALS                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Your laptop    →  reads .env                                       │
│  GitHub Actions →  reads GitHub Secrets                             │
│  Vercel (later) →  reads Vercel Environment Variables               │
│                                                                     │
│  Same keys, stored in 3 places. Never in code.                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Keys & Secrets Summary

| Key | Where it lives | Used by |
|-----|----------------|---------|
| ANTHROPIC_API_KEY | .env (local), GitHub Secrets (cloud) | judge.py |
| SUPABASE_URL | .env, GitHub Secrets | db.py |
| SUPABASE_SERVICE_ROLE_KEY | .env, GitHub Secrets | db.py (write) |
| SUPABASE_PUBLISHABLE_KEY | Web page (public) | Vercel (read-only, Phase 9) |

## Alternative: Agentic Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLAUDE AGENT                                │
│                                                                 │
│  You: "What races are new this week?"                          │
│                                                                 │
│  Claude: [fetches from RunSignup]                               │
│          [checks Supabase for seen races]                       │
│          [judges new ones]                                      │
│          [updates Supabase]                                     │
│          [returns digest in chat]                               │
│                                                                 │
│  Trigger: You ask                                               │
│  Output:  Chat response                                         │
│  Storage: Still needs Supabase (Claude has no memory)           │
└─────────────────────────────────────────────────────────────────┘

Simpler: No Vercel, no GitHub Actions
Trade-off: You must ask (not automatic), no shareable URL
```
