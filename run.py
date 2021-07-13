import subprocess, json, sys, time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

with open('config.json', 'r') as f:
    CONFIG = json.load(f)

proc = subprocess.Popen([sys.executable, 'server.py'], stdout=sys.stdout)
print('Waiting for server to start.')
time.sleep(4)

options = Options()
options.add_argument(f'--kiosk http://{CONFIG["host"]}:{str(CONFIG["port"])}')
driver = webdriver.Firefox(firefox_options=options)
driver.get(f'http://{CONFIG["host"]}:{str(CONFIG["port"])}')
driver.fullscreen_window()
proc.wait()