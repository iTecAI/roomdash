# roomdash
A dashboard for my college room

## Installation
1. Run `sudo bash install.sh` or equivalent to install the required libraries.
2. Acquire a `config.json` like the following:
```json
{
    "owmKey": "openweathermaps api key",
    "mbKey": "mapbox api key",
    "calKey": "path to google calendar service account credentials",
    "persistenceFolder": "persistent",
    "fetchLoopDelay": 60,
    "target": {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "zoom": 8,
        "tileSpan": 1,
        "layers": [
            "precipitation"
        ],
        "locationDisplayName": "NAME OF LOCATION"
    },
    "calendarId": "Calendar id",
    "emailMap": {
        "email": "name"
    },
    "eventCount": 10,
    "host": "localhost",
    "port": 1024,
    "units": "metric"
}
```
3. Get a credentials JSON for the google calendar service account.
4. Run server.py