from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
import json, os
from util import fetchWeatherInformation, Calendar
from multiprocessing import Process
import time
import uvicorn
import imageio

def apiFetchLoop(conf): # Loop through getting API data and saving it locally
    # Initialize calendar
    cal = Calendar(os.path.join(*conf['calKey'].split('/')), conf['calendarId'], emailMap=conf['emailMap'])
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
            includeLayers=conf['target']['layers']
        )
        with open(os.path.join(*conf['persistenceFolder'].split('/'), 'oneCall.json'), 'w') as f:
            json.dump(data, f, indent=4)

        # Build GIF of radar
        if os.path.exists(os.path.join(*conf['persistenceFolder'].split('/'), f'weatherMap{str(conf["radarLoopLength"])}.png')):
            os.remove(os.path.join(*conf['persistenceFolder'].split('/'), f'weatherMap{str(conf["radarLoopLength"])}.png'))
        frames = []
        for frame in range(conf["radarLoopLength"]+1):
            if os.path.exists(os.path.join(*conf['persistenceFolder'].split('/'), f'weatherMap{str(conf["radarLoopLength"]-frame)}.png')):
                os.rename(
                    os.path.join(*conf['persistenceFolder'].split('/'), f'weatherMap{str(conf["radarLoopLength"]-frame)}.png'),
                    os.path.join(*conf['persistenceFolder'].split('/'), f'weatherMap{str(conf["radarLoopLength"]-frame+1)}.png')
                )
                frames.append(imageio.imread(os.path.join(*conf['persistenceFolder'].split('/'), f'weatherMap{str(conf["radarLoopLength"]-frame+1)}.png')))
        with open(os.path.join(*conf['persistenceFolder'].split('/'), 'weatherMap0.png'), 'wb') as f:
            f.write(img)
        frames.insert(0, imageio.imread(os.path.join(*conf['persistenceFolder'].split('/'), 'weatherMap0.png')))
        imageio.mimsave(os.path.join(*conf['persistenceFolder'].split('/'), 'weatherMap.gif'), frames, duration=conf['radarLoopFrameTime'])
        
        # Get events
        events = cal.getEvents(count=conf['eventCount'], days=conf['calendarDaysForward'])
        with open(os.path.join(*conf['persistenceFolder'].split('/'), 'calendarEvents.json'), 'w') as f:
            json.dump(events, f, indent=4)
        
        time.sleep(conf['fetchLoopDelay'])

# Load configuration file @ config.json
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

STARTTIME = time.time()

app = FastAPI()

@app.get('/debug')
async def get_debug():
    return {'target': CONFIG['target'], 'calendar': CONFIG['calendarId']}

@app.get('/data/weatherMap')
async def get_weather_map():
    return FileResponse(os.path.join(*CONFIG['persistenceFolder'].split('/'), 'weatherMap.gif'))

@app.get('/data/weather')
async def get_weather_data():
    with open(os.path.join(*CONFIG['persistenceFolder'].split('/'), 'oneCall.json'), 'r') as f:
        return json.load(f)

@app.get('/data/events')
async def get_events():
    with open(os.path.join(*CONFIG['persistenceFolder'].split('/'), 'calendarEvents.json'), 'r') as f:
        return json.load(f)

# Start loop process and run server if this execution is the main execution
if __name__ == '__main__':
    # Make persistent file directory
    if not os.path.exists(os.path.join(*CONFIG['persistenceFolder'].split('/'))):
        os.mkdir(os.path.join(*CONFIG['persistenceFolder'].split('/')))
    
    # Start fetch loop
    RUNNING_PROCESS = Process(target=apiFetchLoop, name='FetchLoop', args=[CONFIG], daemon=True)
    RUNNING_PROCESS.start()

    # Start REST API
    uvicorn.run('server:app', host=CONFIG['host'], port=CONFIG['port'])
