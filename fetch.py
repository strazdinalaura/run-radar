"""
fetch.py — Phase 1 of Run Radar
Hits RunSignup API, returns SF-area races for the next HORIZON_DAYS.
"""

import requests
from datetime import date, timedelta

# Constants
HORIZON_DAYS = 180
ZIPCODE = "94102"
RADIUS_MILES = 50
RESULTS_PER_PAGE = 50
API_URL = "https://runsignup.com/Rest/races"


def fetch_races():
    """
    Fetch races from RunSignup API.
    Returns list of dicts: {race_id, name, date, city, distance, url, description, price}
    """
    today = date.today()
    end_date = today + timedelta(days=HORIZON_DAYS)

    params = {
        "format": "json",
        "events": "T",  # Include event details (distances, prices)
        "zipcode": ZIPCODE,
        "radius": RADIUS_MILES,
        "start_date": today.isoformat(),
        "end_date": end_date.isoformat(),
        "event_type": "running_race",
        "results_per_page": RESULTS_PER_PAGE,
        "page": 1,
    }

    print(f"Fetching SF-area races ({ZIPCODE}, {RADIUS_MILES}mi radius)")
    print(f"Window: {today} to {end_date} ({HORIZON_DAYS} days)")

    all_races = []
    page = 1

    while True:
        params["page"] = page
        print(f"  Requesting page {page}...")

        resp = requests.get(API_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

        races_on_page = data.get("races", [])
        if not races_on_page:
            break

        for race_wrapper in races_on_page:
            race = race_wrapper.get("race", {})
            parsed = parse_race(race)
            if parsed:
                all_races.append(parsed)

        print(f"    Got {len(races_on_page)} races")

        # If we got fewer than requested, we're on the last page
        if len(races_on_page) < RESULTS_PER_PAGE:
            break
        page += 1

    print(f"Fetched {len(all_races)} races total")
    return all_races


def parse_race(race):
    """
    Extract fields from a single race object.
    Returns dict or None if essential fields missing.
    """
    race_id = race.get("race_id")
    name = race.get("name")

    if not race_id or not name:
        return None

    # Date: use next_date if available
    race_date = race.get("next_date") or race.get("last_date")

    # Location
    address = race.get("address", {})
    city = address.get("city", "")
    state = address.get("state", "")
    location = f"{city}, {state}".strip(", ")

    # URL
    url = race.get("url", "")

    # Description (for judge later)
    description = race.get("description", "") or ""

    # Distance: extract from events if available
    distances = extract_distances(race)

    # Price: try to get from events
    price = extract_price(race)

    return {
        "race_id": race_id,
        "name": name,
        "date": race_date,
        "city": location,
        "distance": distances,
        "url": url,
        "description": description,
        "price": price,
    }


def extract_distances(race):
    """
    Pull distance strings from race events.
    Returns comma-separated string like "5K, 10K, Half Marathon"
    """
    events = race.get("events", [])
    if not events:
        return ""

    distances = []
    seen = set()
    for event in events:
        # Use the distance field (e.g., "5K", "10K", "13.1 Miles")
        dist = event.get("distance", "")
        if dist and dist not in seen:
            distances.append(dist)
            seen.add(dist)

    return ", ".join(distances)


def extract_price(race):
    """
    Try to get registration price. Returns string or empty.
    """
    events = race.get("events", [])
    if not events:
        return ""

    # Take first event's registration price as representative
    for event in events:
        reg_periods = event.get("registration_periods", [])
        for period in reg_periods:
            fee = period.get("race_fee")
            if fee:
                return fee  # Already formatted like "$35.00"

    return ""


def print_races(races):
    """Print races in readable rows."""
    print("\n" + "=" * 80)
    print(f"{'ID':<10} {'DATE':<12} {'CITY':<20} {'DISTANCE':<25} NAME")
    print("=" * 80)

    for r in races:
        race_id = str(r["race_id"])[:9]
        race_date = (r["date"] or "")[:11]
        city = (r["city"] or "")[:19]
        distance = (r["distance"] or "")[:24]
        name = r["name"][:40]
        print(f"{race_id:<10} {race_date:<12} {city:<20} {distance:<25} {name}")

    print("=" * 80)


if __name__ == "__main__":
    races = fetch_races()
    print_races(races)
