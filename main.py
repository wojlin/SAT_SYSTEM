from datetime import datetime, timedelta
import threading
import signal
import json
import time
import ast
import sys
import os

import globals
import utils
from managers import info_manager, \
    flyby_manager, \
    map_manager, \
    tle_manager, \
    decode_manager, \
    logging_manager, \
    api_manager, \
    status_manager, \
    rotator_manager

threads = []
start_date = datetime.now()


def draw_board(table_name, drawing_settings, vertical_offset):
    print('\033[H', end='', flush=True)
    print(f'\033[{vertical_offset};0H', end='', flush=True)
    if table_name == 'map':
        sat_file = ast.literal_eval(utils.read_file('config/tle.json'))
        sats = tle_manager.read_tle(sat_file)
        table, height = map_manager.draw_box(satellites=sats,
                                             drawing_settings=drawing_settings,
                                             width=globals.WIDTH,
                                             padding=globals.PADDING)

    elif table_name == 'flyby':
        sat_file = ast.literal_eval(utils.read_file('config/tle.json'))
        sats = tle_manager.read_tle(sat_file)
        hours = int(json.loads(utils.read_file('config/setup.json'))["drawing_settings"]["flyby_config"]['hours_ahead'])
        angle = int(
            json.loads(utils.read_file('config/setup.json'))["drawing_settings"]["flyby_config"]['minimal_angle'])
        amount = int(
            json.loads(utils.read_file('config/setup.json'))["drawing_settings"]["flyby_config"]['display_amount'])
        filtered_list = flyby_manager.get_flyby_filtered_list(sats, datetime.utcnow(),
                                                              datetime.utcnow() + timedelta(hours=hours), angle)
        table, height = flyby_manager.draw_box(filtered_list, amount,
                                               drawing_settings=drawing_settings,
                                               width=globals.WIDTH,
                                               padding=globals.PADDING)
    elif table_name == 'info':
        sat_file = ast.literal_eval(utils.read_file('config/tle.json'))
        sats = tle_manager.read_tle(sat_file)
        table, height = info_manager.draw_box(sats,
                                              drawing_settings=drawing_settings,
                                              width=globals.WIDTH,
                                              padding=globals.PADDING)

    elif table_name == 'status':

        table, height = status_manager.draw_box(drawing_settings=drawing_settings,
                                                width=globals.WIDTH,
                                                padding=globals.PADDING)

    else:
        raise Exception("module does not exist")

    sys.stdout.write(table)

    return height


def manage_tle():
    if json.loads(utils.read_file('config/setup.json'))["tle_update"]['update'] is True:
        interval = float(json.loads(utils.read_file('config/setup.json'))["tle_update"]['update_interval'])
        pre_sat_file = ast.literal_eval(utils.read_file('config/tle.json'))
        tle_update_manager_thread = threading.Thread(target=tle_manager.tle_update_manager, daemon=True,
                                                     args=(interval, pre_sat_file,))
        threads.append(tle_update_manager_thread)
        tle_update_manager_thread.start()


def draw_boards(drawing_settings):
    os.system('clear')
    schedule = {key: {"offset": 0, "timeout": globals.BOARDS[key]} for key in globals.BOARDS}
    heights = [0,]
    for key, val in globals.BOARDS.items():
        height = draw_board(key, drawing_settings=drawing_settings, vertical_offset=heights[-1])
        height_sum = heights[-1] + height + 2
        schedule[key]["offset"] = heights[-1]
        heights.append(height_sum)
    return schedule


def manage_box_drawing(drawing_settings):
    timeouts_load = json.loads(utils.read_file('config/setup.json'))["console_update"]
    timeouts = dict(timeouts_load).copy()
    last_width = os.get_terminal_size().columns

    schedule = draw_boards(drawing_settings)
    tick = float(json.loads(utils.read_file('config/setup.json'))["tick_speed"])
    while True:
        time.sleep(tick)
        globals.WIDTH = os.get_terminal_size().columns

        if last_width != globals.WIDTH:
            schedule = draw_boards(drawing_settings)
            last_width = os.get_terminal_size().columns

        for key in timeouts:
            timeouts[key] = timeouts[key] - tick
            if timeouts[key] <= 0:
                draw_board(key, drawing_settings=drawing_settings, vertical_offset=schedule[key]['offset'])
                timeouts[key] = timeouts_load[key]


def manage_decode():
    if json.loads(utils.read_file('config/setup.json'))["decode_settings"]['decode'] is True:
        sat_file = ast.literal_eval(utils.read_file('config/tle.json'))
        sats = tle_manager.read_tle(sat_file)

        delete_temp = bool(json.loads(utils.read_file('config/setup.json'))["decode_settings"]['delete_temp_files'])
        temp = str(json.loads(utils.read_file('config/setup.json'))["decode_settings"]['decode_temp_path'])
        output = str(json.loads(utils.read_file('config/setup.json'))["decode_settings"]['output_dir_path'])
        hours = int(json.loads(utils.read_file('config/setup.json'))["drawing_settings"]["flyby_config"]['hours_ahead'])
        angle = int(
            json.loads(utils.read_file('config/setup.json'))["drawing_settings"]["flyby_config"]['minimal_angle'])
        tle_update_manager_thread = threading.Thread(target=decode_manager.decode_manager, daemon=True,
                                                     kwargs={'sats': sats,
                                                             "t_in": datetime.utcnow(),
                                                             "t_out": datetime.utcnow() + timedelta(hours=hours),
                                                             "angle": angle,
                                                             'delete_temp': delete_temp,
                                                             'temp': temp,
                                                             'output': output})
        threads.append(tle_update_manager_thread)
        tle_update_manager_thread.start()


def manage_api():
    if json.loads(utils.read_file('config/setup.json'))["api_settings"]['use_api'] is True:
        api_manager_thread = threading.Thread(target=api_manager.start_api, daemon=True)
        threads.append(api_manager_thread)
        api_manager_thread.start()


def manage_rotator():
    if json.loads(utils.read_file('config/setup.json'))["decode_settings"]['use_rotator'] is True:
        rotator_manager_thread = threading.Thread(target=rotator_manager.tcp_manager, daemon=True)
        threads.append(rotator_manager_thread)
        rotator_manager_thread.start()


def program_exit(signum, frame):
    os.system('clear')
    sys.stdout.write("\033[?25h")
    print(f"SAT SYSTEM started on {start_date} and ended on {datetime.now()}")
    sys.exit()


def main():
    print('\033[?25l', end="")
    globals.LOGGER = logging_manager.manage_logging()
    manage_api()
    manage_tle()
    manage_decode()
    manage_rotator()
    signal.signal(signal.SIGINT, program_exit)
    manage_box_drawing(globals.ANSI_DRAWING_SETTINGS)


if __name__ == '__main__':
    main()
