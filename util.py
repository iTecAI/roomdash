import requests, json
from pyowm.commons.tile import Tile
from pyowm.utils.geo import Point
from PIL import Image
import io
from concurrent.futures import ThreadPoolExecutor
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import date, datetime, timedelta
import pytz

def default(dct, key, default=None):
    try:
        return dct[key]
    except KeyError:
        return default

def _load_layer(includeLayers, zoom, i, keys):
    layer = []
    for x in includeLayers:
        layer.insert(0, Image.open(io.BytesIO(requests.get(
            f'https://tile.openweathermap.org/map/{x}/{zoom}/{i[0]}/{i[1]}.png', {'appid': keys['owm']}).content)))
    polygon = Tile.tile_coords_to_bbox(i[0], i[1], zoom)
    backdrop = Image.open(
        io.BytesIO(
            requests.get(
                f'https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v11/static/[{",".join([str(n) for n in polygon])}]/256x256/',
                params={
                    'access_token': keys['mapbox'],
                    'attribution': 'false',
                    'logo': 'false'
                }
            ).content
        )
    )
    for l in layer:
        backdrop.paste(l, (0,0), l)
    return backdrop

def fetchWeatherInformation(latitude, longitude, zoom, keys={
    'owm': '',
    'mapbox': ''
}, tileSpan=1, includeLayers=['precipitation']):
    oneCallData = requests.get('https://api.openweathermap.org/data/2.5/onecall', params={
        'lat': latitude,
        'lon': longitude,
        'appid': keys['owm']
    }).json()

    tileCoords = Tile.tile_coords_for_point(Point(longitude, latitude), zoom)
    if tileSpan == 0:
        allTileCoords = [tileCoords]
        tileRelatives = [(0, 0)]
    else:
        atc = [[(tileCoords[0]+x, tileCoords[1]+y) for y in range(-1 *
                                                                  tileSpan, tileSpan+1)] for x in range(-1*tileSpan, tileSpan+1)]
        allTileCoords = []
        tileRelatives = []
        for c in atc:
            allTileCoords.extend(c)
            tileRelatives.extend(
                [(i[0]-tileCoords[0], i[1]-tileCoords[1]) for i in c])

    with ThreadPoolExecutor(max_workers=16) as executor:
        results = [executor.submit(_load_layer, includeLayers, zoom, allTileCoords[c], keys) for c in range(len(allTileCoords))]
    tileImages = {tileRelatives[c]:results[c].result() for c in range(len(tileRelatives))}
    
    resultant = Image.new('RGBA', [256+512*tileSpan, 256+512*tileSpan], (0,0,0,0))
    for img in tileImages.keys():
        resultant.paste(
            tileImages[img], 
            (img[0]*256 + tileSpan*256, img[1]*256 + tileSpan*256)
        )
    resultantBytes = io.BytesIO(b'')
    resultant.save(resultantBytes, format='png')

    return oneCallData, resultantBytes.getvalue()

class Calendar:
    def __init__(self, credentials_file, cid, emailMap={}):
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        SERVICE_ACCOUNT_FILE = credentials_file
        self.credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = build('calendar', 'v3', credentials=self.credentials)
        self.cid = cid
        self.emailMap = emailMap

    def getEvents(self, count=25, days=7):
        now = datetime.utcnow().isoformat() + 'Z'
        endDate = (datetime.utcnow()+timedelta(days=days)).isoformat() + 'Z'
        calendar = self.service.events().list(
            calendarId=self.cid,
            maxResults=count,
            orderBy='startTime',
            singleEvents=True,
            timeMin=now,
            timeMax=endDate
        ).execute()
        events = calendar['items']
        ret = []
        for e in events:
            if 'dateTime' in e['start'].keys():
                start = datetime.fromisoformat(e['start']['dateTime'])
                if 'timeZone' in e['start'].keys():
                    start = pytz.timezone(e['start']['timeZone']).localize(start)
                else:
                    start = pytz.timezone('UTC').localize(start)
            else:
                start = datetime.fromisoformat(e['start']['date'])
                start = pytz.timezone('UTC').localize(start)

            if 'dateTime' in e['end'].keys():
                end = datetime.fromisoformat(e['end']['dateTime'])
                if 'timeZone' in e['end'].keys():
                    end = pytz.timezone(e['end']['timeZone']).localize(end)
                else:
                    end = pytz.timezone('UTC').localize(end)
            else:
                end = datetime.fromisoformat(e['end']['date'])
                end = pytz.timezone('UTC').localize(end)
            item = {
                'name': e['summary'],
                'status': e['status'],
                'description': default(e, 'description'),
                'start': start.isoformat(),
                'end': end.isoformat(),
                'link': e['htmlLink'],
                'creator': default(self.emailMap, e['creator']['email'], e['creator']['email'])
            }
            ret.append(item)
        return ret