import utils
import time
import json
import os

LOGGER = None
LAST_ACTION = f"program startup at {time.strftime('%Y-%m-%d %H:%M:%S')}"
ACTION_LOG = [LAST_ACTION]
POS = json.loads(utils.read_file('config/setup.json'))["ground_station"]
TEMP = str(json.loads(utils.read_file('config/setup.json'))["decode_settings"]['decode_temp_path'])
PATH = os.path.abspath('')
WIDTH = 180
HEIGHT = 45
HOST = json.loads(utils.read_file('config/setup.json'))["api_settings"]["host"]
PORT = json.loads(utils.read_file('config/setup.json'))["api_settings"]["port"]

DRAWING_SETTINGS = {}

for key in json.loads(utils.read_file('config/setup.json'))['drawing_settings']:
    DRAWING_SETTINGS[key] = utils.read_config(("drawing_settings", key))

