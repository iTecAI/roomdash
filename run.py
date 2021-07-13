import subprocess, webbrowser, json, sys, time

with open('config.json', 'r') as f:
    CONFIG = json.load(f)

proc = subprocess.Popen([sys.executable, 'server.py'], stdout=sys.stdout)
print('Waiting for server to start.')
time.sleep(4)
webbrowser.open(f'http://{CONFIG["host"]}:{str(CONFIG["port"])}')
print('Stopped with code '+str(proc.wait()))