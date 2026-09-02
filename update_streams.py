import json
import urllib.request
from datetime import datetime
from bs4 import BeautifulSoup

CHANNEL = "peppseez"  # Change to the streamer's Twitch handle
URL = f"https://twitchtracker.com/{CHANNEL}/streams"

# Use custom headers so TwitchTracker doesn't block the request
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
req = urllib.request.Request(URL, headers=headers)

try:
    html = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(html, 'html.parser')

    # Load existing streams.json
    try:
        with open('streams.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    # Extract dates from the stream history table
    # TwitchTracker renders streams inside a table with dates
    rows = soup.find_all('tr')
    for row in rows:
        time_tag = row.find('time')
        if time_tag and 'datetime' in time_tag.attrs:
            # Format date as YYYY-MM-DD
            raw_date = time_tag['datetime'].split('T')[0]
            
            # If it's on TwitchTracker's stream list, mark as "streamed"
            if raw_date not in data or data[raw_date] == "empty":
                data[raw_date] = "streamed"

    # Save back to streams.json
    with open('streams.json', 'w') as f:
        json.dump(data, f, indent=2, sort_keys=True)

    print("Successfully updated streams.json")

except Exception as e:
    print(f"Error fetching TwitchTracker: {e}")
