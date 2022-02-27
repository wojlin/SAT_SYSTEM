import utils
import time
import json
import os

LAST_ACTION = f"program startup at {time.strftime('%Y-%m-%d %H:%M:%S')}"
ACTION_LOG = [LAST_ACTION]
POS = json.loads(utils.read_file('config/setup.json'))["ground_station"]
PATH = os.path.abspath('')
WIDTH = 180
HEIGHT = 45
