from datetime import datetime, timedelta
import threading
import json
import time
import ast
import sys

import globals
import utils
from managers import info_manager, flyby_manager, map_manager, tle_manager, decode_manager, logging_manager, api_manager


def draw_board(table_name, drawing_settings, first_time, add_height):
    if table_name == 'map':
        sat_file = ast.literal_eval(utils.read_file('config/tle.json'))
        sats = tle_manager.read_tle(sat_file)
        table, height = map_manager.draw_box(satellites=sats, drawing_settings=drawing_settings)
        if not first_time:
            for i in range(height + add_height):
                sys.stdout.write("\033[F\033[K")
        sys.stdout.write(table)
        sys.stdout.write('\n')
    elif table_name == 'flyby':
        sat_file = ast.literal_eval(utils.read_file('config/tle.json'))
        sat_file = ast.literal_eval(utils.read_file('config/tle.json'))
        sats = tle_manager.read_tle(sat_file)
        hours = int(json.loads(utils.read_file('config/setup.json'))["flyby_prediction_settings"]['hours_ahead'])
        angle = int(json.loads(utils.read_file('config/setup.json'))["flyby_prediction_settings"]['minimal_angle'])
        amount = int(json.loads(utils.read_file('config/setup.json'))["flyby_prediction_settings"]['display_amount'])
        filtered_list = flyby_manager.get_flyby_filtered_list(sats, datetime.utcnow(),
                                                              datetime.utcnow() + timedelta(hours=hours), angle)
        table, height = flyby_manager.draw_box(filtered_list, amount, drawing_settings=drawing_settings)
        if not first_time:
            for i in range(height + add_height):
                sys.stdout.write("\033[F\033[K")
        sys.stdout.write(table)
        sys.stdout.write('\n')
    elif table_name == 'info':
        sat_file = ast.literal_eval(utils.read_file('config/tle.json'))
        sats = tle_manager.read_tle(sat_file)
        table, height = info_manager.draw_box(sats, drawing_settings=drawing_settings)
        if not first_time:
            for i in range(height + add_height):
                sys.stdout.write("\033[F\033[K")
        sys.stdout.write(table)
        sys.stdout.write('\n')
    elif table_name == 'last':
        height = 1
        for i in range(height + add_height):
            sys.stdout.write("\033[F\033[K")

        spaces = [100, 20]

        text_buffer = utils.add_col(f"LAST ACTION: {globals.LAST_ACTION}", spaces[0]) + \
                      utils.add_col(f"RADIO:", spaces[1])
        target = f"http://{globals.HOST}:{globals.PORT}"
        server = f"SERVER: \u001b]8;;{target}\u001b\\{target}\u001b]8;;\u001b\\"
        text_buffer += (' ' * (globals.WIDTH - len(text_buffer) - len(target) - len("SERVER:")) + server)

        sys.stdout.write(str(text_buffer + '\n'))

    else:
        raise Exception("module does not exist")
    return height


def manage_tle():
    if json.loads(utils.read_file('config/setup.json'))["tle_update"]['update'] is True:
        interval = float(json.loads(utils.read_file('config/setup.json'))["tle_update"]['update_interval'])
        pre_sat_file = ast.literal_eval(utils.read_file('config/tle.json'))
        tle_update_manager_thread = threading.Thread(target=tle_manager.tle_update_manager,
                                                     args=(interval, pre_sat_file,))
        tle_update_manager_thread.start()


def manage_box_drawing(drawing_settings):
    heights = [['map', draw_board('map', drawing_settings, first_time=True, add_height=0)],
               ['flyby', draw_board('flyby', drawing_settings, first_time=True, add_height=0)],
               ['info', draw_board('info', drawing_settings, first_time=True, add_height=0)],
               ['last', draw_board('last', drawing_settings, first_time=True, add_height=0)]]

    timeouts_load = json.loads(utils.read_file('config/setup.json'))["console_update"]
    timeouts = json.loads(utils.read_file('config/setup.json'))["console_update"]

    while True:
        time.sleep(0.1)
        for key in timeouts:
            timeouts[key] = timeouts[key] - 0.1
            if timeouts[key] <= 0:
                index = 0
                add_height = 0
                for i in range(len(heights)):
                    if heights[i][0] == key:
                        index = i
                for i in range(index + 1, len(heights)):
                    add_height += heights[i][1]
                draw_board(key, first_time=False, add_height=add_height, drawing_settings=drawing_settings)
                for i in range(index + 1, len(heights)):
                    draw_board(heights[i][0], first_time=True, add_height=0, drawing_settings=drawing_settings)
                timeouts[key] = timeouts_load[key]


def manage_decode():
    if json.loads(utils.read_file('config/setup.json'))["decode_settings"]['decode'] is True:
        sat_file = ast.literal_eval(utils.read_file('config/tle.json'))
        sats = tle_manager.read_tle(sat_file)

        delete_temp = bool(json.loads(utils.read_file('config/setup.json'))["decode_settings"]['delete_temp_files'])
        temp = str(json.loads(utils.read_file('config/setup.json'))["decode_settings"]['decode_temp_path'])
        output = str(json.loads(utils.read_file('config/setup.json'))["decode_settings"]['output_dir_path'])
        hours = int(json.loads(utils.read_file('config/setup.json'))["flyby_prediction_settings"]['hours_ahead'])
        angle = int(json.loads(utils.read_file('config/setup.json'))["flyby_prediction_settings"]['minimal_angle'])
        tle_update_manager_thread = threading.Thread(target=decode_manager.decode_manager,
                                                     kwargs={'sats': sats,
                                                             "t_in": datetime.utcnow(),
                                                             "t_out": datetime.utcnow() + timedelta(hours=hours),
                                                             "angle": angle,
                                                             'delete_temp': delete_temp,
                                                             'temp': temp,
                                                             'output': output})
        tle_update_manager_thread.start()


def manage_api():
    if json.loads(utils.read_file('config/setup.json'))["api_settings"]['use_api'] is True:
        api_manager_thread = threading.Thread(target=api_manager.start_api)
        api_manager_thread.start()


def main():
    globals.LOGGER = logging_manager.manage_logging()
    manage_api()
    manage_tle()
    manage_decode()
    manage_box_drawing(globals.ANSI_DRAWING_SETTINGS)


if __name__ == '__main__':
    main()
