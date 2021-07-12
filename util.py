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
import qrcode
import base64

def default(dct, key, default=None): # Load key from dct, or default on failure
    try:
        return dct[key]
    except KeyError:
        return default

def _load_layer(includeLayers, zoom, i, keys): # Load a single tile of the stitched image
    layer = []
    for x in includeLayers:
        layer.insert(0, Image.open(io.BytesIO(requests.get(
            f'https://tile.openweathermap.org/map/{x}/{zoom}/{i[0]}/{i[1]}.png', {'appid': keys['owm']}).content))) # Get each layer from OWM
    polygon = Tile.tile_coords_to_bbox(i[0], i[1], zoom) # Get bounding box

    # Load satellite image
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

    # Paste layers together
    for l in layer:
        backdrop.paste(l, (0,0), l)
    return backdrop

# Get weather information
def fetchWeatherInformation(latitude, longitude, zoom, keys={
    'owm': '',
    'mapbox': ''
}, tileSpan=1, includeLayers=['precipitation'], units='standard'):
    oneCallData = requests.get('https://api.openweathermap.org/data/2.5/onecall', params={
        'lat': latitude,
        'lon': longitude,
        'appid': keys['owm'],
        'units': units
    }).json() # Get oneCall JSON data

    tileCoords = Tile.tile_coords_for_point(Point(longitude, latitude), zoom) # Get tile coordinates from lat/lon/zoom
    
    # Assemble stitch map from tileSpan
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

    # Fetch each tile image
    with ThreadPoolExecutor(max_workers=16) as executor:
        results = [executor.submit(_load_layer, includeLayers, zoom, allTileCoords[c], keys) for c in range(len(allTileCoords))]
    tileImages = {tileRelatives[c]:results[c].result() for c in range(len(tileRelatives))}
    
    # Stitch tile images together into the final image
    resultant = Image.new('RGBA', [256+512*tileSpan, 256+512*tileSpan], (0,0,0,0))
    for img in tileImages.keys():
        resultant.paste(
            tileImages[img], 
            (img[0]*256 + tileSpan*256, img[1]*256 + tileSpan*256)
        )
    resultantBytes = io.BytesIO(b'')
    resultant.save(resultantBytes, format='png')

    return oneCallData, resultantBytes.getvalue()

class Calendar: # Object for getting calendar events
    def __init__(self, credentials_file, cid, emailMap={}):
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        SERVICE_ACCOUNT_FILE = credentials_file

        # Load credentials
        self.credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = build('calendar', 'v3', credentials=self.credentials)
        self.cid = cid
        self.emailMap = emailMap

    def getEvents(self, count=25, days=7): # Get list of events
        # Get start and end of results to fetch
        now = datetime.utcnow().isoformat() + 'Z'
        endDate = (datetime.utcnow()+timedelta(days=days)).isoformat() + 'Z'

        # Get raw list of events
        calendar = self.service.events().list(
            calendarId=self.cid,
            maxResults=count,
            orderBy='startTime',
            singleEvents=True,
            timeMin=now,
            timeMax=endDate
        ).execute()
        events = calendar['items']

        # Assemble event list into standard format
        ret = []
        for e in events:
            # Assemble start and end entries
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
            
            # Build dict and add it to the return
            qrobj = qrcode.QRCode(version=1, box_size=2)
            qrobj.add_data(e['htmlLink'])
            qrfile = io.BytesIO(b'')
            qrobj.make_image(fit=True).save(qrfile, format='png')

            data_url = 'data:image/png;base64,'+base64.b64encode(qrfile.getvalue()).decode('utf-8')

            item = {
                'name': e['summary'],
                'status': e['status'],
                'description': default(e, 'description'),
                'start': start.isoformat(),
                'end': end.isoformat(),
                'link': e['htmlLink'],
                'creator': default(self.emailMap, e['creator']['email'], e['creator']['email']),
                'qrcode': data_url
            }
            ret.append(item)
        return ret