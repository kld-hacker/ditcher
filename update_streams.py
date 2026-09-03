import json
import requests
from datetime import datetime, timezone

CHANNEL_NAME = "peppseez"
JSON_FILE = "streams.json"

# Public Twitch Web App Credentials
CLIENT_ID = 'kimne78kx3ncx6br8ac42060chm450'

def get_guest_access_token():
    """Generates an OAuth token using public Twitch Client ID."""
    try:
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": CLIENT_ID,
            "grant_type": "client_credentials"
        }
        # Request token
        res = requests.post(url, params=params, timeout=10)
        res.raise_for_status()
        return res.json().get("access_token")
    except Exception as e:
        print(f"Failed to get access token: {e}")
        return None

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

    # Get guest access token
    token = get_guest_access_token()
    
    headers = {
        'Client-ID': CLIENT_ID,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'

    # Query Twitch API
    try:
        url = f"https://api.twitch.tv/helix/streams?user_login={CHANNEL_NAME}"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        res_data = response.json()

        is_live = len(res_data.get('data', [])) > 0

        if is_live:
            data[today_str] = "streamed"
            print(f"[{today_str}] Channel IS live! Recorded as 'streamed'.")
        else:
            # If already marked streamed today, keep it
            if data.get(today_str) == "streamed":
                print(f"[{today_str}] Channel offline now, but was already marked 'streamed' today.")
            # Only mark as 'ditched' on the final check of the window (18:00 UTC / 20:00 Italian time)
            elif current_hour_utc >= 18:
                data[today_str] = "ditched"
                print(f"[{today_str}] Channel offline at end of stream window. Recorded as 'ditched'.")
            else:
                print(f"[{today_str}] Channel offline. Waiting for remaining hourly checks before marking 'ditched'.")

    except Exception as e:
        print(f"Error querying Twitch API: {e}")
        return

    # Save updated JSON file
    with open(JSON_FILE, 'w') as f:
        json.dump(data, f, indent=2, sort_keys=True)

    print("Successfully updated streams.json")

if __name__ == "__main__":
    check_and_update()
