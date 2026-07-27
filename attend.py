"""
attend.py — Mark races you're attending + generate calendar.

Usage:
    python attend.py review        # review today's new races with judgments
    python attend.py review 2026-07-20  # review a specific day
    python attend.py list          # show upcoming races
    python attend.py add <race_id> # mark as attending
    python attend.py remove <race_id>
    python attend.py calendar      # generate races.ics
"""

import sys
from pathlib import Path
from db import get_upcoming_races, get_attending_races, mark_attending, get_new_races_with_judgments

ICS_PATH = Path(__file__).parent / "races.ics"


def review_races(first_seen_date=None):
    """Review new races with their judgments."""
    races = get_new_races_with_judgments(first_seen_date)

    if not races:
        print(f"No new races for {first_seen_date or 'today'}.")
        return

    from datetime import date
    display_date = first_seen_date or date.today().isoformat()
    print(f"\n{'='*70}")
    print(f"NEW RACES — {display_date} — {len(races)} found")
    print(f"{'='*70}")

    for r in races:
        fit = (r.get("fit") or "?").upper()
        att = " [ATTENDING]" if r.get("attending") else ""

        print(f"\n[{fit}] {r['name']}{att}")
        print(f"      {r['date']} | {r.get('city', '')} | {r.get('distance', '')}")
        if r.get("reasoning"):
            print(f"      → {r['reasoning']}")

        url = r.get("url", "")
        if url and not url.startswith("http"):
            url = "https://runsignup.com" + url
        if url:
            print(f"      {url}")
        print(f"      ID: {r['race_id']}")

    print(f"\n{'='*70}")
    print("To mark as attending: python attend.py add <race_id>")
    print(f"{'='*70}\n")


def list_races():
    """List upcoming races with attending status."""
    races = get_upcoming_races(30)
    if not races:
        print("No upcoming races found.")
        return

    print(f"{'ID':<12} {'DATE':<12} {'ATT':^3} {'NAME'}")
    print("-" * 70)
    for r in races:
        att = " * " if r.get("attending") else ""
        name = r["name"][:45]
        print(f"{r['race_id']:<12} {r['date']:<12} {att:^3} {name}")

    print(f"\n* = attending. Use 'python attend.py add <race_id>' to mark.")


def add_race(race_id):
    """Mark a race as attending."""
    mark_attending(race_id, True)
    print(f"Marked {race_id} as attending.")


def remove_race(race_id):
    """Unmark a race."""
    mark_attending(race_id, False)
    print(f"Removed {race_id} from attending.")


def generate_calendar():
    """Generate .ics file for attending races."""
    races = get_attending_races()

    if not races:
        print("No races marked as attending. Use 'python attend.py add <race_id>' first.")
        return

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Run Radar//Races//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Run Radar Races",
    ]

    for race in races:
        # Convert MM/DD/YYYY to YYYYMMDD
        from datetime import datetime
        try:
            dt = datetime.strptime(race["date"], "%m/%d/%Y")
            date_str = dt.strftime("%Y%m%d")
        except (ValueError, TypeError):
            continue
        uid = f"{race['race_id']}@runradar"
        url = race.get("url", "")
        if url and not url.startswith("http"):
            url = "https://runsignup.com" + url

        summary = f"{race['name']} ({race['distance']})"
        location = race.get("city", "")
        description = race.get("description", "")[:200] if race.get("description") else ""
        if url:
            description = f"{url}\\n\\n{description}" if description else url

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTART;VALUE=DATE:{date_str}",
            f"DTEND;VALUE=DATE:{date_str}",
            f"SUMMARY:{summary}",
            f"LOCATION:{location}",
            f"DESCRIPTION:{description}",
            "END:VEVENT",
        ])

    lines.append("END:VCALENDAR")

    ICS_PATH.write_text("\r\n".join(lines))
    print(f"Generated {ICS_PATH} with {len(races)} race(s).")
    print(f"\nTo use: Import this file into your calendar app, or copy contents to a GitHub Gist.")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "review":
        date_arg = sys.argv[2] if len(sys.argv) > 2 else None
        review_races(date_arg)
    elif cmd == "list":
        list_races()
    elif cmd == "add" and len(sys.argv) > 2:
        add_race(sys.argv[2])
    elif cmd == "remove" and len(sys.argv) > 2:
        remove_race(sys.argv[2])
    elif cmd == "calendar":
        generate_calendar()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
