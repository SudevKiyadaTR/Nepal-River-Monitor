#!/usr/bin/env python3
"""Fetch 7 days of timestamped (~10-min resolution) series data for every river station and
merge it into a single time series store, keyed by station then by reading timestamp.

Safe to run daily: existing timestamps are left untouched unless DHM republishes a new value
for one (then it's overwritten), and new timestamps are simply added. Never overwrites the
whole file blindly.
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from fetch_series import fetch_series, new_session

STATIONS_URL = "https://dhm.gov.np/home/getAPIData/3"
OUT = Path(__file__).resolve().parent.parent / "data" / "river_series.json"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def main():
    stations = [s for s in requests.get(STATIONS_URL, timeout=30).json()["river_watch"] if s.get("series_id")]
    session, csrf = new_session()

    store = json.loads(OUT.read_text()) if OUT.exists() else {}

    added = updated = 0
    for i, station in enumerate(stations, 1):
        station_id, series_id, name = station["id"], station["series_id"], station["name"]
        try:
            points = fetch_series(session, csrf, series_id, TODAY, period="4", station_id=station_id)
        except Exception as e:
            print(f"[{i}/{len(stations)}] {name}: FAILED ({e})")
            continue

        entry = store.setdefault(str(series_id), {"station_id": station_id, "name": name, "readings": {}})
        entry["station_id"], entry["name"] = station_id, name
        readings = entry["readings"]
        for point in points:
            ts, value = point["datetime"], point["value"]
            if ts in readings and readings[ts] != value:
                updated += 1
            elif ts not in readings:
                added += 1
            readings[ts] = value

        print(f"[{i}/{len(stations)}] {name}: ok ({len(points)} points)")
        time.sleep(0.3)

    for entry in store.values():
        entry["readings"] = dict(sorted(entry["readings"].items()))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(store, indent=2, sort_keys=True))
    print(f"done: {added} new readings, {updated} updated readings")


if __name__ == "__main__":
    main()
