#!/usr/bin/env python3
"""Fetch historical daily-period series data for every river station and append to a JSONL time series."""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from fetch_series import fetch_series, new_session

STATIONS_URL = "https://dhm.gov.np/home/getAPIData/3"
OUT = Path(__file__).resolve().parent.parent / "data" / "dhm_river_series.jsonl"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def main():
    stations = [s for s in requests.get(STATIONS_URL, timeout=30).json()["river_watch"] if s.get("series_id")]
    session, csrf = new_session()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("a") as f:
        for i, station in enumerate(stations, 1):
            station_id, series_id, name = station["id"], station["series_id"], station["name"]
            try:
                series = fetch_series(session, csrf, series_id, TODAY, period="3", station_id=station_id)
            except Exception as e:
                print(f"[{i}/{len(stations)}] {name}: FAILED ({e})")
                continue

            record = {
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "station_id": station_id,
                "series_id": series_id,
                "name": name,
                "date_requested": TODAY,
                "data": series,
            }
            f.write(json.dumps(record) + "\n")
            print(f"[{i}/{len(stations)}] {name}: ok")
            time.sleep(0.3)


if __name__ == "__main__":
    main()
