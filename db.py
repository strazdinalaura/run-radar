"""
db.py — Phase 2 of Run Radar
SQLite snapshot table + diff. Turns fetches into events.
"""

import sqlite3
from datetime import date
from pathlib import Path

DB_PATH = Path(__file__).parent / "seen.db"


def get_connection():
    """Get SQLite connection, creating table if needed."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS races (
            race_id INTEGER PRIMARY KEY,
            name TEXT,
            date TEXT,
            city TEXT,
            distance TEXT,
            url TEXT,
            description TEXT,
            price TEXT,
            first_seen TEXT
        )
    """)
    conn.commit()
    return conn


def sync_races(races):
    """
    Insert-if-absent. Returns list of newly inserted records (events).

    Args:
        races: list of dicts from fetch_races()

    Returns:
        list: the new records that were inserted (events)
    """
    conn = get_connection()
    cursor = conn.cursor()

    today = date.today().isoformat()
    new_records = []
    already_seen = 0

    for race in races:
        # Check if exists
        cursor.execute("SELECT 1 FROM races WHERE race_id = ?", (race["race_id"],))
        if cursor.fetchone():
            already_seen += 1
            continue

        # Insert new record
        cursor.execute("""
            INSERT INTO races (race_id, name, date, city, distance, url, description, price, first_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            race["race_id"],
            race["name"],
            race["date"],
            race["city"],
            race["distance"],
            race["url"],
            race["description"],
            race["price"],
            today,
        ))
        # Track the new record with first_seen added
        new_record = dict(race)
        new_record["first_seen"] = today
        new_records.append(new_record)

    conn.commit()
    conn.close()

    print(f"Sync complete: {len(new_records)} new, {already_seen} already seen")
    return new_records


def get_events():
    """
    Get events = races seen for the first time today.

    Returns:
        list of dicts (race records where first_seen = today)
    """
    conn = get_connection()
    cursor = conn.cursor()

    today = date.today().isoformat()
    cursor.execute("SELECT * FROM races WHERE first_seen = ?", (today,))
    rows = cursor.fetchall()

    conn.close()

    # Convert to list of dicts
    events = [dict(row) for row in rows]
    print(f"Events today: {len(events)}")
    return events


def get_record_count():
    """Get total records in table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM races")
    count = cursor.fetchone()[0]
    conn.close()
    return count


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
