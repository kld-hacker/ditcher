import json
import os
import requests
from datetime import datetime, timezone

CHANNEL_NAME = "peppseez"

# Official Twitch Helix API Endpoint
URL = f"https://api.twitch.tv/helix/streams?user_login={CHANNEL_NAME}"

# Public Client ID used by the Twitch web client
HEADERS = {
    'Client-ID': 'kimne78kx3ncx6br8ac42060chm450',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

def update_tracker():
    today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    # 1. Load current JSON database
    try:
        with open('streams.json', 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    # 2. Check if Twitch says the channel is currently LIVE
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        res_data = response.json()

        is_live = len(res_data.get('data', [])) > 0

        if is_live:
            # Mark today as streamed
            data[today_str] = "streamed"
            print(f"[{today_str}] Channel is currently LIVE! Recorded as 'streamed'.")
        else:
            # If no status exists for today, set default status
            # Adjust 'ditched' vs 'off' depending on your preference logic
            if today_str not in data or data[today_str] == "empty":
                data[today_str] = "ditched"
                print(f"[{today_str}] Channel was offline at check. Recorded as 'ditched'.")

    except Exception as e:
        print(f"Error fetching Twitch API: {e}")
        return

    # 3. Save back to streams.json
    with open('streams.json', 'w') as f:
        json.dump(data, f, indent=2, sort_keys=True)

    print("Successfully updated streams.json")

if __name__ == "__main__":
    update_tracker()
