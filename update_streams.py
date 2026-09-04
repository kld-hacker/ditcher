import json
import requests
from datetime import datetime, timezone

CHANNEL_NAME = "peppseez"
JSON_FILE = "streams.json"

# Headers mimicking a standard browser request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

def check_and_update():
    now = datetime.now(timezone.utc)
    today_str = now.strftime('%Y-%m-%d')
    current_hour_utc = now.hour

    # Load existing JSON
    try:
        with open(JSON_FILE, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    # Check live status via HTML scraping
    try:
        url = f"https://www.twitch.tv/{CHANNEL_NAME}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        # Twitch embeds "isLiveBroadcast" in the page metadata when a channel is live
        is_live = "isLiveBroadcast" in response.text

        # Helper to safely read the status regardless of string or object format
        existing_entry = data.get(today_str)
        existing_status = existing_entry.get("status") if isinstance(existing_entry, dict) else existing_entry

        if is_live:
            # Preserve existing custom reason if present, otherwise set default object structure
            if isinstance(existing_entry, dict):
                data[today_str]["status"] = "streamed"
            else:
                data[today_str] = {
                    "status": "streamed",
                    "reason": ""
                }
            print(f"[{today_str}] Channel IS live! Recorded as 'streamed'.")
        else:
            # If already marked streamed today, keep it
            if existing_status == "streamed":
                print(f"[{today_str}] Channel offline now, but was already marked 'streamed' today.")
            # Only mark as 'ditched' on the final check of the window (18:00 UTC / 20:00 Italian time)
            elif current_hour_utc >= 18:
                if isinstance(existing_entry, dict):
                    data[today_str]["status"] = "ditched"
                else:
                    data[today_str] = {
                        "status": "ditched",
                        "reason": ""
                    }
                print(f"[{today_str}] Channel offline at end of stream window. Recorded as 'ditched'.")
            else:
                print(f"[{today_str}] Channel offline. Waiting for remaining hourly checks before marking 'ditched'.")

    except Exception as e:
        print(f"Error fetching channel page: {e}")
        return

    # Save updated JSON file
    with open(JSON_FILE, 'w') as f:
        json.dump(data, f, indent=2, sort_keys=True)

    print("Successfully updated streams.json")

if __name__ == "__main__":
    check_and_update()
