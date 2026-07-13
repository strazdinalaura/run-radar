"""
judge.py — Phase 3 of Run Radar
Single LLM call per race. Returns fit judgment.

Real API mode (USE_STUB = False). Stub kept for offline testing.
Stub baseline on eval_labels.md: 21/29 (72%).
"""

import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Toggle: True = mock rules, False = real API
USE_STUB = False

MODEL = "claude-haiku-4-5-20251001"
PREFS_PATH = Path(__file__).parent / "prefs.md"

_prefs_cache = None


def load_prefs():
    """Load preferences from prefs.md (cached)."""
    global _prefs_cache
    if _prefs_cache is None:
        _prefs_cache = PREFS_PATH.read_text()
        print(f"Loaded prefs from {PREFS_PATH.name}")
    return _prefs_cache


def _stub_judge(race):
    """
    Rule-based mock judgment based on prefs.md criteria.
    Returns {fit, reasoning} without API call.
    """
    name = (race.get("name") or "").lower()
    city = (race.get("city") or "").lower()
    distance = (race.get("distance") or "").lower()
    price_str = race.get("price") or ""
    description = (race.get("description") or "").lower()

    # Parse price
    price = 0
    if price_str:
        match = re.search(r"\$?([\d.]+)", price_str)
        if match:
            price = float(match.group(1))

    # Check distance - hard no ONLY if no short option exists
    # Parse all distances
    import re as re2
    mile_matches = re2.findall(r'([\d.]+)\s*miles?', distance, re2.IGNORECASE)
    km_matches = re2.findall(r'(\d+)k\b', distance, re2.IGNORECASE)

    has_short_option = False
    has_only_long = False

    # Check miles
    for m in mile_matches:
        if float(m) < 10:
            has_short_option = True
        else:
            has_only_long = True

    # Check km (5K = ~3mi, 10K = ~6mi, both OK)
    for k in km_matches:
        if int(k) <= 10:
            has_short_option = True

    # Reject only if it's marathon/ultra-only OR only long distances
    long_only = ["marathon", "ultra", "50k", "50 miles", "30k"]
    if any(d in distance for d in long_only) and not has_short_option:
        return {"fit": "no", "reasoning": "Marathon/ultra only - not ready yet"}

    if has_only_long and not has_short_option:
        return {"fit": "no", "reasoning": "Only long distance options (10+ miles)"}

    # Negative signals - check early
    is_novelty = any(w in name for w in ["virtual", "costume", "turkey", "santa", "halloween", "zombie", "reindeer"])
    if is_novelty:
        return {"fit": "no", "reasoning": "Costume/novelty themed race - skip"}

    # Check if trail race - these get special treatment
    is_trail = any(w in name + description for w in ["trail", "ridge", "creek", "res run", "reservoir"])

    # Location logic
    is_sf = "san francisco" in city
    is_bart_accessible = any(loc in city for loc in ["oakland", "alameda", "berkeley"])
    is_marin = any(loc in city for loc in ["marin", "stinson", "sausalito", "mill valley", "san rafael", "muir"])
    is_east_bay_burbs = any(loc in city for loc in ["castro valley", "orinda", "lafayette", "walnut creek", "concord", "pleasant hill"])

    # Marin = NO (weekend logistics nightmare)
    if is_marin:
        return {"fit": "no", "reasoning": "Marin - weekend transit unreliable"}

    # Trail races - special handling
    if is_trail:
        if is_sf:
            return {"fit": "yes", "reasoning": "SF trail race - perfect"}
        elif is_east_bay_burbs or is_bart_accessible:
            # Lafayette Res, Bear Creek, etc. - close enough for Uber
            if "lafayette" in name.lower() or "res" in name.lower():
                return {"fit": "yes", "reasoning": "Trail race at reservoir - worth the trip"}
            return {"fit": "maybe", "reasoning": "Trail race - worth the logistics"}
        else:
            return {"fit": "no", "reasoning": "Trail race but too far without car"}

    # Non-trail, non-SF/BART = no
    if not is_sf and not is_bart_accessible:
        return {"fit": "no", "reasoning": "Location requires car - not accessible"}

    # Positive signals for SF/BART races
    positive = []
    if any(w in name + description for w in ["scenic", "waterfront", "park", "view"]):
        positive.append("scenic")
    if any(w in name + description for w in ["community", "local", "charity", "cause"]):
        positive.append("community vibe")

    # Distance signals
    is_sweet_spot = "10k" in distance or "6.2" in distance or "5k" in distance or "3.1" in distance
    is_odd_distance = any(d in distance for d in ["4 miles", "7k", "2 miles", "4k"])

    if is_sf:
        if is_sweet_spot and positive:
            return {"fit": "yes", "reasoning": f"SF + {positive[0]} + good distance"}
        elif is_sweet_spot:
            return {"fit": "maybe", "reasoning": "SF + good distance, check vibes"}
        elif is_odd_distance:
            return {"fit": "maybe", "reasoning": "SF but odd distance - depends on vibes"}
        else:
            return {"fit": "maybe", "reasoning": "SF location, worth a look"}

    # BART-accessible (Oakland, Alameda, Berkeley)
    if is_bart_accessible:
        if positive and is_sweet_spot:
            return {"fit": "maybe", "reasoning": f"BART-accessible + {positive[0]}"}
        else:
            return {"fit": "no", "reasoning": "BART-accessible but not compelling enough"}

    return {"fit": "no", "reasoning": "No compelling signals"}


def judge_race(race):
    """
    Judge one race against preferences.
    Uses stub or real API based on USE_STUB flag.
    """
    load_prefs()  # Ensure prefs loaded

    print(f"Judging: {race['name'][:50]}...", end=" ")

    if USE_STUB:
        result = _stub_judge(race)
    else:
        import anthropic

        prefs = load_prefs()
        race_summary = f"""Race: {race['name']}
Date: {race['date']}
Location: {race['city']}
Distance: {race['distance']}
Price: {race['price'] or 'Not listed'}
URL: {race['url']}

Description:
{race.get('description', 'No description')[:1000]}"""

        prompt = f"""Based on the runner's preferences below, judge if this race is a good fit.

RUNNER'S PREFERENCES:
{prefs}

RACE TO JUDGE:
{race_summary}

Respond with JSON only, no other text:
{{"fit": "yes" or "no" or "maybe", "reasoning": "one sentence why"}}"""

        client = anthropic.Anthropic()
        response = client.messages.create(
            model=MODEL,
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.content[0].text.strip()
        try:
            result = json.loads(text)
        except json.JSONDecodeError:
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                result = json.loads(text.strip())
            else:
                result = {"fit": "maybe", "reasoning": f"Parse error: {text[:100]}"}

    print(f"→ {result['fit']} ({result['reasoning'][:60]})")
    return result


def judge_races(races):
    """
    Judge multiple races. Returns list of (race, judgment) tuples.
    """
    load_prefs()  # Pre-load once
    results = []
    for race in races:
        judgment = judge_race(race)
        results.append((race, judgment))
    return results


if __name__ == "__main__":
    # Test with a few races from the database
    import sqlite3
    from db import DB_PATH

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get 5 sample races
    cursor.execute("SELECT * FROM races LIMIT 5")
    rows = cursor.fetchall()
    conn.close()

    print(f"\nTesting judge on {len(rows)} races:\n")

    for row in rows:
        race = dict(row)
        judgment = judge_race(race)
        print()

    print("\nDone.")
