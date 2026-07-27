"""
db.py — Phase 5 of Run Radar
Supabase backend. Replaces SQLite.
"""

import os
from datetime import date
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

_supabase = None

def get_client():
    """Get Supabase client (singleton)."""
    global _supabase
    if _supabase is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env")
        _supabase = create_client(url, key)
    return _supabase


def sync_races(races):
    """
    Insert-if-absent. Returns list of newly inserted records (events).

    Args:
        races: list of dicts from fetch_races()

    Returns:
        list: the new records that were inserted (events)
    """
    supabase = get_client()
    today = date.today().isoformat()

    # Get existing race_ids
    result = supabase.table("races").select("race_id").execute()
    existing_ids = {r["race_id"] for r in result.data}

    new_records = []
    already_seen = 0

    for race in races:
        if race["race_id"] in existing_ids:
            already_seen += 1
            continue

        # Insert new record
        record = {
            "race_id": race["race_id"],
            "name": race["name"],
            "date": race["date"],
            "city": race["city"],
            "distance": race["distance"],
            "url": race["url"],
            "description": race["description"],
            "price": race["price"],
            "logo_url": race.get("logo_url", ""),
            "first_seen": today,
        }
        supabase.table("races").insert(record).execute()

        # Track the new record
        new_record = dict(race)
        new_record["first_seen"] = today
        new_records.append(new_record)

    print(f"Sync complete: {len(new_records)} new, {already_seen} already seen")
    return new_records


def save_judgment(race_id, fit, reasoning):
    """Save a judgment to Supabase."""
    supabase = get_client()
    today = date.today().isoformat()

    record = {
        "race_id": race_id,
        "fit": fit,
        "reasoning": reasoning,
        "judged_at": today,
    }
    supabase.table("judgments").insert(record).execute()


def get_events():
    """
    Get events = races seen for the first time today.

    Returns:
        list of dicts (race records where first_seen = today)
    """
    supabase = get_client()
    today = date.today().isoformat()

    result = supabase.table("races").select("*").eq("first_seen", today).execute()

    print(f"Events today: {len(result.data)}")
    return result.data


def mark_attending(race_id, attending=True):
    """Mark a race as attending or not attending."""
    supabase = get_client()
    supabase.table("races").update({"attending": attending}).eq("race_id", race_id).execute()


def get_attending_races():
    """Get all races marked as attending, ordered by date."""
    supabase = get_client()
    result = supabase.table("races").select("*").eq("attending", True).order("date").execute()
    return result.data


def get_upcoming_races(limit=20):
    """Get upcoming races, ordered by date. Filters out past races."""
    from datetime import datetime
    supabase = get_client()
    result = supabase.table("races").select("*").limit(500).execute()

    today = date.today()
    upcoming = []
    for r in result.data:
        if not r.get("date"):
            continue
        try:
            race_date = datetime.strptime(r["date"], "%m/%d/%Y").date()
            if race_date >= today:
                r["_sort_date"] = race_date
                upcoming.append(r)
        except ValueError:
            continue

    upcoming.sort(key=lambda x: x["_sort_date"])
    return upcoming[:limit]


def get_new_races_with_judgments(first_seen_date=None):
    """Get races added on a date with their judgments. Defaults to today."""
    supabase = get_client()
    if first_seen_date is None:
        first_seen_date = date.today().isoformat()

    races = supabase.table("races").select("*").eq("first_seen", first_seen_date).execute()
    judgments = supabase.table("judgments").select("*").execute()

    # Index judgments by race_id
    judgment_map = {j["race_id"]: j for j in judgments.data}

    # Combine
    results = []
    for race in races.data:
        j = judgment_map.get(race["race_id"], {})
        results.append({
            **race,
            "fit": j.get("fit"),
            "reasoning": j.get("reasoning"),
        })

    # Sort: yes first, then maybe, then no/None
    order = {"yes": 0, "maybe": 1, "no": 2, None: 3}
    results.sort(key=lambda x: order.get(x["fit"], 3))
    return results


def get_record_count():
    """Get total records in table."""
    supabase = get_client()
    result = supabase.table("races").select("race_id", count="exact").execute()
    return result.count


def is_cold_start():
    """Check if this is the first run (no records yet)."""
    return get_record_count() == 0


if __name__ == "__main__":
    # Test: run with current fetch
    from fetch import fetch_races

    cold = is_cold_start()
    print(f"Cold start: {cold}")
    print(f"Records before: {get_record_count()}")
    print()

    races = fetch_races()
    print()

    events = sync_races(races)
    print(f"Records after: {get_record_count()}")
    print()

    if cold:
        print("First run (priming). No events surfaced.")
    elif events:
        print(f"Events ({len(events)} new races):")
        for e in events:
            print(f"  {e['race_id']} | {e['date']} | {e['name'][:50]}")
    else:
        print("No new races since last run.")
