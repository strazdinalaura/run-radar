# Run Radar Architecture

## Current State (Local)

```
┌─────────────────────────────────────────────────────────────────┐
│                        YOUR LAPTOP                              │
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ fetch.py │───▶│  db.py   │───▶│ judge.py │───▶│ main.py  │  │
│  │          │    │          │    │          │    │          │  │
│  │ RunSignup│    │ seen.db  │    │ Claude   │    │ digest   │  │
│  │ API      │    │ (SQLite) │    │ Haiku    │    │ output   │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│       │                │               │               │        │
│       ▼                ▼               ▼               ▼        │
│   External         Local file      Anthropic       Terminal     │
│   API call         storage         API call        + file       │
└─────────────────────────────────────────────────────────────────┘

Trigger: You run `python3 main.py`
Output:  Terminal + digest.md
```

## Planned State (Cloud)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   GITHUB    │     │  SUPABASE   │     │   VERCEL    │
│   Actions   │     │  Database   │     │   Web Page  │
│             │     │             │     │             │
│ Runs daily  │────▶│ races table │◀────│ Reads data  │
│ at 6am      │     │ judgments   │     │ shows digest│
│             │     │             │     │             │
│ main.py     │     │ Cloud       │     │ Phone-      │
│ in cloud    │     │ storage     │     │ friendly    │
└─────────────┘     └─────────────┘     └─────────────┘
      │                                        │
      ▼                                        ▼
  Anthropic API                          Anyone with
  (judge races)                          the URL

Trigger: Automatic (cron)
Output:  Web page at lauras-race-radar.vercel.app
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

## Keys & Secrets

| Key | Where it lives | Used by |
|-----|----------------|---------|
| ANTHROPIC_API_KEY | .env (local), GitHub Secrets (cloud) | judge.py |
| SUPABASE_URL | .env, GitHub Secrets | db.py |
| SUPABASE_SERVICE_KEY | .env, GitHub Secrets | db.py (write) |
| SUPABASE_ANON_KEY | Web page (public) | Vercel (read-only) |

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
