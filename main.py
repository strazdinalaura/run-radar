"""
main.py — Run Radar pipeline
The runner: fetch → sync → judge new races.

Usage: python3 main.py
Output: terminal summary + Supabase
"""

from datetime import date

from db import is_cold_start, sync_races, save_judgment
from fetch import fetch_races
from judge import judge_races


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

    print_summary(today, new_races, surfaced, passed)


def print_summary(today, new_races, surfaced, passed):
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


if __name__ == "__main__":
    run()
