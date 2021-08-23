from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import json, os
from util import fetchWeatherInformation, Calendar
from multiprocessing import Process
import time
import uvicorn
import datetime
import icmplib

def apiFetchLoop(conf): # Loop through getting API data and saving it locally
    # Initialize calendar
    calendars = [Calendar(os.path.join(*conf['calKey'].split('/')), c['id'], emailMap=conf['emailMap'], tz=conf['timezone'], name=c['name'], color=c['color']) for c in conf['calendars']]
    while True:
        # Get weather info
        data, img = fetchWeatherInformation(
            conf['target']['latitude'],
            conf['target']['longitude'],
            conf['target']['zoom'],
            keys={
                'owm': conf['owmKey'],
                'mapbox': conf['mbKey']
            },
            tileSpan=conf['target']['tileSpan'],
            includeLayers=conf['target']['layers'],
            units=conf['units']
        )
        with open(os.path.join(*conf['persistenceFolder'].split('/'), 'oneCall.json'), 'w') as f:
            json.dump(data, f, indent=4)

        with open(os.path.join(*conf['persistenceFolder'].split('/'), 'weatherMap.png'), 'wb') as f:
            f.write(img)

        # Get events
        events = []
        for cal in calendars:
            events.extend(cal.getEvents(count=conf['eventCount']))
        events = sorted(events, key=lambda event: datetime.datetime.fromisoformat(event['start']).timestamp())
        with open(os.path.join(*conf['persistenceFolder'].split('/'), 'calendarEvents.json'), 'w') as f:
            json.dump(events, f, indent=4)
        
        time.sleep(conf['fetchLoopDelay'])

def pingLoop(conf):
    while True:
        serverdata = conf['servers'][:]
        for i in serverdata:
            try:
                pingdata = icmplib.ping(i['address'], privileged=False)
                i['alive'] = pingdata.is_alive
                i['ping'] = str(pingdata.avg_rtt) + 's'
            except icmplib.NameLookupError:
                i['alive'] = False
                i['ping'] = 'N/A'
        with open(os.path.join(*conf['persistenceFolder'].split('/'), 'pingData.json'), 'w') as f:
            json.dump(serverdata, f, indent=4)
        time.sleep(conf['pingLoopDelay'])


# Load configuration file @ config.json
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

STARTTIME = time.time()

app = FastAPI()

@app.get('/debug')
async def get_debug():
    return {'target': CONFIG['target'], 'calendars': CONFIG['calendars'], 'units': CONFIG['units']}

@app.get('/data/weatherMap')
async def get_weather_map():
    return FileResponse(os.path.join(*CONFIG['persistenceFolder'].split('/'), 'weatherMap.png'), headers={
        'Cache-Control': 'no-cache'
    })

@app.get('/data/weather')
async def get_weather_data():
    with open(os.path.join(*CONFIG['persistenceFolder'].split('/'), 'oneCall.json'), 'r') as f:
        return json.load(f)

@app.get('/data/events')
async def get_events():
    with open(os.path.join(*CONFIG['persistenceFolder'].split('/'), 'calendarEvents.json'), 'r') as f:
        return json.load(f)

@app.get('/data/pings')
async def get_pings():
    with open(os.path.join(*CONFIG['persistenceFolder'].split('/'), 'pingData.json'), 'r') as f:
        return json.load(f)

app.mount('/s', StaticFiles(directory='web'), name='static')

@app.get('/')
async def get_root():
    return FileResponse(os.path.join('web', 'index.html'), media_type='text/html')

# Start loop process and run server if this execution is the main execution
if __name__ == '__main__':
    # Make persistent file directory
    if not os.path.exists(os.path.join(*CONFIG['persistenceFolder'].split('/'))):
        os.mkdir(os.path.join(*CONFIG['persistenceFolder'].split('/')))
    
    # Start fetch loop
    RUNNING_PROCESS = Process(target=apiFetchLoop, name='FetchLoop', args=[CONFIG], daemon=True)
    RUNNING_PROCESS.start()
    RUNNING_PROCESS2 = Process(target=pingLoop, name='PingLoop', args=[CONFIG], daemon=True)
    RUNNING_PROCESS2.start()

    # Start REST API
    uvicorn.run('server:app', host=CONFIG['host'], port=CONFIG['port'], access_log=False)
