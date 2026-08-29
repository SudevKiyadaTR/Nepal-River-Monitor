#!/usr/bin/env python3
"""Scrape historical river-watch data for a single station (series) from DHM.

period: 1=Point (1 day, timestamped), 2=Hourly (1 day, hour buckets), 3=Daily (7 days, no
per-reading timestamps), 4=7 Days Point (7 days, ~10-min readings, each with a datetime)
"""
import json
import re
import sys

import requests

BASE = "https://dhm.gov.np"


def new_session(station_id=4913):
    """A logged session + matching CSRF token, reusable across many fetch_series calls."""
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0"})
    page = s.get(f"{BASE}/hydrology/hms-Single/{station_id}", timeout=20)
    csrf = re.search(r'name="csrf_test_name" value="([a-f0-9]+)"', page.text).group(1)
    return s, csrf


def fetch_series(session, csrf, series_id, date, period="4", station_id=4913):
    resp = session.post(
        f"{BASE}/site/getRiverWatchBySeriesId_Single",
        data={"csrf_test_name": csrf, "date": date, "period": period, "seriesid": series_id},
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{BASE}/hydrology/hms-Single/{station_id}",
            "Origin": BASE,
        },
        timeout=20,
    )
    resp.raise_for_status()
    body = resp.json()

    match = re.search(r"var river = '(.*)';", body["data"]["chart"])
    raw = match.group(1).encode().decode("unicode_escape")
    return json.loads(raw)


if __name__ == "__main__":
    series_id, date = sys.argv[1], sys.argv[2]
    session, csrf = new_session()
    print(json.dumps(fetch_series(session, csrf, series_id, date), indent=2))
