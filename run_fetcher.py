#!/usr/bin/env python3
"""Fetch exchange rate every N minutes and store in PostgreSQL. Set FETCH_INTERVAL_MINUTES or FETCH_INTERVAL_SECONDS in .env."""
import os
import sys
import time
from pathlib import Path

_root = Path(__file__).resolve().parent
sys.path.insert(0, str(_root))
os.chdir(_root)
if (_root / ".env").exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_root / ".env")
    except ImportError:
        pass

from api_integration.exchange_rate import fetch_and_store_data


def main():
    interval_sec = os.environ.get("FETCH_INTERVAL_SECONDS")
    if interval_sec is not None:
        interval_sec = max(10, min(int(interval_sec), 86400))
        print(f"Fetching exchange rate every {interval_sec} second(s). Stop with Ctrl+C.")
        sleep_sec = interval_sec
    else:
        interval = int(os.environ.get("FETCH_INTERVAL_MINUTES", "5"))
        interval = max(1, min(interval, 1440))
        print(f"Fetching exchange rate every {interval} minute(s). Stop with Ctrl+C.")
        sleep_sec = 60 * interval
    try:
        while True:
            fetch_and_store_data()
            time.sleep(sleep_sec)
    except KeyboardInterrupt:
        print("Stopped.")

if __name__ == "__main__":
    main()
