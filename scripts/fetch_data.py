#!/usr/bin/env python3
"""Fetch DHM API snapshot and append it as one line to the time series file."""
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://dhm.gov.np/home/getAPIData/3"
OUT = Path(__file__).resolve().parent.parent / "data" / "dhm_type3.jsonl"


def main():
    with urllib.request.urlopen(URL, timeout=30) as resp:
        payload = json.load(resp)

    record = {"fetched_at": datetime.now(timezone.utc).isoformat(), "data": payload}

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("a") as f:
        f.write(json.dumps(record) + "\n")


if __name__ == "__main__":
    main()
