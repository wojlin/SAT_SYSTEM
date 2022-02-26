import utils
import time
import json

LAST_ACTION = f"program startup at {time.strftime('%Y-%m-%d %H:%M:%S')}"
ACTION_LOG = [LAST_ACTION]
POS = json.loads(utils.read_file('config/setup.json'))["ground_station"]
WIDTH = 180
HEIGHT = 45
