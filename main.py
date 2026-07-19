"""
main.py — Phase 4 of Run Radar
The runner: fetch → sync → judge new races → digest.

Usage: python3 main.py
Output: terminal digest + appended entry in digest.md
"""

from datetime import date
from pathlib import Path

from db import is_cold_start, sync_races, save_judgment
from fetch import fetch_races
from judge import judge_races

DIGEST_PATH = Path(__file__).parent / "digest.md"


def run():
    today = date.today().isoformat()
    cold = is_cold_start()

    races = fetch_races()
    new_races = sync_races(races)

    if cold:
        print(f"\nFirst run: primed {len(new_races)} races. No judging on a cold start.")
        print("Run again later — only races new since this baseline get judged.")
        return

    if not new_races:
        print("\nNo new races since last run. Radar quiet.")
        return

    print(f"\nJudging {len(new_races)} new race(s)...\n")
    results = judge_races(new_races)

    # Save judgments to Supabase
    for race, judgment in results:
        save_judgment(race["race_id"], judgment["fit"], judgment["reasoning"])

    surfaced = [(r, j) for r, j in results if j["fit"] in ("yes", "maybe")]
    passed = [(r, j) for r, j in results if j["fit"] == "no"]

    print_digest(today, new_races, surfaced, passed)
    write_digest(today, new_races, surfaced, passed)


def print_digest(today, new_races, surfaced, passed):
    print("=" * 70)
    print(f"RUN RADAR — {today} — {len(new_races)} new, {len(surfaced)} worth a look")
    print("=" * 70)

    if not surfaced:
        print("Nothing matches your prefs this time.")
    for race, judgment in surfaced:
        tag = "YES  " if judgment["fit"] == "yes" else "MAYBE"
        price = f" | {race['price']}" if race["price"] else ""
        print(f"\n[{tag}] {race['name']}")
        print(f"        {race['date']} | {race['city']} | {race['distance']}{price}")
        print(f"        {judgment['reasoning']}")
        if race["url"]:
            u = race["url"]
            print(f"        {u if u.startswith('http') else 'https://runsignup.com' + u}")

    if passed:
        print(f"\nPassed on {len(passed)}: " + "; ".join(r["name"][:40] for r, _ in passed))
    print("=" * 70)


def write_digest(today, new_races, surfaced, passed):
    """Append this run's digest to digest.md (newest entry at top of file body)."""
    lines = [f"\n## {today} — {len(new_races)} new, {len(surfaced)} surfaced\n"]

    if not surfaced:
        lines.append("Nothing matched prefs.\n")
    for race, judgment in surfaced:
        price = f" | {race['price']}" if race["price"] else ""
        u = race["url"] or ""
        if u and not u.startswith("http"):
            u = "https://runsignup.com" + u
        url = f" | [signup]({u})" if u else ""
        lines.append(
            f"- **{judgment['fit'].upper()}** — {race['name']} — "
            f"{race['date']} | {race['city']} | {race['distance']}{price}{url}\n"
            f"  - {judgment['reasoning']}\n"
        )

    if passed:
        lines.append(f"- Passed on {len(passed)}: " + "; ".join(r["name"][:40] for r, _ in passed) + "\n")

    if DIGEST_PATH.exists():
        existing = DIGEST_PATH.read_text()
        # Insert new entry right after the header line
        header, _, body = existing.partition("\n")
        content = header + "\n" + "".join(lines) + body
    else:
        content = "# Run Radar digest\n" + "".join(lines)

    DIGEST_PATH.write_text(content)
    print(f"Digest appended to {DIGEST_PATH.name}")


if __name__ == "__main__":
    run()
