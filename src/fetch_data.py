import os
import time
import requests
import pandas as pd
from datetime import date, timedelta
from dotenv import load_dotenv

os.environ.pop("SSLKEYLOGFILE", None)  # neutralize a background process that breaks HTTPS requests

load_dotenv()
API_KEY = os.getenv("NASA_API_KEY")
BASE_URL = "https://api.nasa.gov/neo/rest/v1/feed"


def daterange_chunks(start, end, chunk_days=7):
    """Break one big date range into 7-day pieces, since that's NASA's limit per request."""
    current = start
    while current <= end:
        chunk_end = min(current + timedelta(days=chunk_days - 1), end)
        yield current, chunk_end
        current = chunk_end + timedelta(days=1)


def fetch_neo_data(start_date, end_date):
    rows = []

    for chunk_start, chunk_end in daterange_chunks(start_date, end_date):
        params = {
            "start_date": chunk_start.isoformat(),
            "end_date": chunk_end.isoformat(),
            "api_key": API_KEY,
        }
        resp = requests.get(BASE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

        for approach_date, asteroids in data["near_earth_objects"].items():
            for a in asteroids:
                close_approach = a["close_approach_data"][0] if a["close_approach_data"] else {}
                rows.append({
                    "id": a["id"],
                    "name": a["name"],
                    "approach_date": approach_date,
                    "absolute_magnitude_h": a["absolute_magnitude_h"],
                    "est_diameter_min_km": a["estimated_diameter"]["kilometers"]["estimated_diameter_min"],
                    "est_diameter_max_km": a["estimated_diameter"]["kilometers"]["estimated_diameter_max"],
                    "is_potentially_hazardous": a["is_potentially_hazardous_asteroid"],
                    "relative_velocity_kph": float(close_approach.get("relative_velocity", {}).get("kilometers_per_hour", 0)),
                    "miss_distance_km": float(close_approach.get("miss_distance", {}).get("kilometers", 0)),
                    "miss_distance_lunar": float(close_approach.get("miss_distance", {}).get("lunar", 0)),
                    "orbiting_body": close_approach.get("orbiting_body"),
                })

        time.sleep(1)

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = fetch_neo_data(date(2025, 1, 1), date(2025, 12, 31))  # one year
    os.makedirs("data/raw", exist_ok=True)
    df.to_csv("data/raw/neo_test.csv", index=False)
    print(f"Saved {len(df)} rows.")