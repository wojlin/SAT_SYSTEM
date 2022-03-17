import utils
import time
import json
import os


class options:
    def __init__(self, option_type, render, args):
        self.type = option_type
        self.render = render
        self.option = {}

        for arg in args:
            self.option[arg] = args[arg]

    def __repr__(self):
        return json.dumps(self.option, sort_keys=True, indent=4)


LOGGER = None
LAST_ACTION = f"program startup at {time.strftime('%Y-%m-%d %H:%M:%S')}"
ACTION_LOG = [LAST_ACTION]
POS = json.loads(utils.read_file('config/setup.json'))["ground_station"]
TEMP = str(json.loads(utils.read_file('config/setup.json'))["decode_settings"]['decode_temp_path'])
OUTPUT = str(json.loads(utils.read_file('config/setup.json'))["decode_settings"]['output_dir_path'])
PATH = os.path.abspath('')
WIDTH = 180
HEIGHT = 45
HOST = json.loads(utils.read_file('config/setup.json'))["api_settings"]["host"]
PORT = json.loads(utils.read_file('config/setup.json'))["api_settings"]["port"]

ANSI_DRAWING_SETTINGS = options('drawing_settings', 'ansi', json.loads(utils.read_file('config/setup.json'))['drawing_settings'])
HTML_DRAWING_SETTINGS = options('drawing_settings', 'html', json.loads(utils.read_file('config/setup.json'))['drawing_settings'])