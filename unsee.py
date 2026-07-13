"""
unsee.py — test helper for Phase 4
Deletes N random races from seen.db so the next main.py run re-detects
them as "new". For testing the diff → judge → digest pipeline.

Usage: python3 unsee.py [N]   (default 10)
"""

import sqlite3
import sys

from db import DB_PATH


def unsee(n=10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT race_id, name FROM races ORDER BY RANDOM() LIMIT ?", (n,)
    )
    victims = cursor.fetchall()

    if not victims:
        print("seen.db is empty — nothing to unsee. Run main.py first to prime it.")
        return

    for race_id, name in victims:
        cursor.execute("DELETE FROM races WHERE race_id = ?", (race_id,))
        print(f"  unseen: {race_id} | {name[:55]}")

    conn.commit()
    conn.close()
    print(f"\nDeleted {len(victims)} races. Next main.py run will re-detect them as new.")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    unsee(n)
