"""
eval.py — Phase 3 of Run Radar
Score judge.py against hand-labeled races in eval_labels.md.

Usage: python3 eval.py
Works with stub or real API (whatever judge.USE_STUB says).
"""

import os
import re
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

from judge import judge_race, USE_STUB

load_dotenv()

LABELS_PATH = Path(__file__).parent / "config" / "eval_labels.md"
VALID_LABELS = {"yes", "no", "maybe"}


def get_client():
    """Get Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)


def load_labels():
    """
    Parse eval_labels.md into [{name, date, label}].
    Tolerates label typos like 'n0' -> 'no'.
    """
    text = LABELS_PATH.read_text()
    entries = []
    current = None

    for line in text.splitlines():
        # Numbered race line: " 1. Race Name"
        m = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if m:
            current = {"name": m.group(1).strip(), "date": None, "label": None}
            continue
        if current is None:
            continue
        # Detail line: "09/27/2026 | Martinez, CA | ..."
        m = re.match(r"^\s*(\d{2}/\d{2}/\d{4})\s*\|", line)
        if m:
            current["date"] = m.group(1)
            continue
        # Label line
        m = re.match(r"^\s*Label:\s*(\S+)", line)
        if m:
            label = m.group(1).lower().replace("0", "o")  # n0 -> no
            if label not in VALID_LABELS:
                print(f"  WARNING: bad label '{m.group(1)}' for {current['name']} — skipping")
            else:
                current["label"] = label
                entries.append(current)
            current = None

    return entries


def find_race(supabase, name):
    """Look up race in Supabase by exact name, fall back to prefix match."""
    # Try exact match
    result = supabase.table("races").select("*").eq("name", name).limit(1).execute()
    if result.data:
        return result.data[0]

    # Fall back to prefix match (first 20 chars)
    result = supabase.table("races").select("*").ilike("name", name[:20] + "%").limit(1).execute()
    return result.data[0] if result.data else None


def run_eval():
    labels = load_labels()
    print(f"Loaded {len(labels)} labeled races")
    print(f"Judge mode: {'STUB (rule-based)' if USE_STUB else 'REAL API'}\n")

    supabase = get_client()

    results = []  # (name, expected, got)
    missing = []

    for entry in labels:
        race = find_race(supabase, entry["name"])
        if race is None:
            missing.append(entry["name"])
            continue
        judgment = judge_race(race)
        results.append((entry["name"], entry["label"], judgment["fit"], judgment["reasoning"]))

    # Score
    correct = sum(1 for _, exp, got, _ in results if exp == got)
    total = len(results)

    # Confusion matrix
    order = ["yes", "maybe", "no"]
    matrix = {e: {g: 0 for g in order} for e in order}
    for _, exp, got, _ in results:
        matrix[exp][got] += 1

    print("\n" + "=" * 70)
    print(f"ACCURACY: {correct}/{total} ({100 * correct / total:.0f}%)")
    print("=" * 70)
    header = "expected / got"
    print(f"\n{header:<16}" + "".join(f"{g:>8}" for g in order))
    for e in order:
        print(f"{e:<16}" + "".join(f"{matrix[e][g]:>8}" for g in order))

    # Misses
    misses = [(n, e, g, r) for n, e, g, r in results if e != g]
    if misses:
        print(f"\nMISSES ({len(misses)}):")
        for name, exp, got, reasoning in misses:
            print(f"  {name[:45]:<47} expected={exp:<6} got={got:<6} ({reasoning[:50]})")

    if missing:
        print(f"\nNOT IN DB ({len(missing)}): " + "; ".join(missing))

    return results


if __name__ == "__main__":
    run_eval()
