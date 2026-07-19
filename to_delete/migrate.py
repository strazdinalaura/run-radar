"""
migrate.py — One-time migration from seen.db to Supabase.
Run once, then delete this file.
"""

import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

DB_PATH = Path(__file__).parent / "seen.db"

def migrate():
    # Connect to Supabase
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        print("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env")
        return

    supabase = create_client(url, key)

    # Read from SQLite
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM races")
    rows = cursor.fetchall()
    conn.close()

    print(f"Found {len(rows)} races in seen.db")

    # Insert into Supabase
    races = [dict(row) for row in rows]

    # Insert in batches of 100 (Supabase limit)
    batch_size = 100
    inserted = 0

    for i in range(0, len(races), batch_size):
        batch = races[i:i + batch_size]
        result = supabase.table("races").insert(batch).execute()
        inserted += len(batch)
        print(f"Inserted {inserted}/{len(races)}")

    print(f"\nMigration complete: {len(races)} races moved to Supabase")
    print("Verify in your Supabase dashboard: Table Editor → races")

if __name__ == "__main__":
    migrate()
