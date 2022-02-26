from datetime import datetime, timedelta
import threading
import json
import time
import ast
import sys

import globals
import utils
from satellites import satellite
import flyby_manager
import info_manager
import map_manager
import tle_manager


def draw_board(table_name, first_time, add_height):
    height = 0
    if table_name == 'map':
        sat_file = ast.literal_eval(utils.read_file('config/tle.json'))
        sats = tle_manager.read_tle(sat_file)
        table, height = map_manager.draw_map(satellites=sats, pathes=3600)
        if not first_time:
            for i in range(height + add_height):
                sys.stdout.write("\033[F\033[K")
        sys.stdout.write(table)
        sys.stdout.write('\n')
    elif table_name == 'flyby':
        sat_file = ast.literal_eval(utils.read_file('config/tle.json'))
        sats = tle_manager.read_tle(sat_file)
        filtered_list = flyby_manager.get_flyby_filtered_list(sats, datetime.utcnow(),
                                                              datetime.utcnow() + timedelta(hours=13), 15)
        table, height = flyby_manager.draw_list(filtered_list, 5)
        if not first_time:
            for i in range(height + add_height):
                sys.stdout.write("\033[F\033[K")
        sys.stdout.write(table)
        sys.stdout.write('\n')
    elif table_name == 'info':
        sat_file = ast.literal_eval(utils.read_file('config/tle.json'))
        sats = tle_manager.read_tle(sat_file)
        table, height = info_manager.draw_info(sats)
        if not first_time:
            for i in range(height + add_height):
                sys.stdout.write("\033[F\033[K")
        sys.stdout.write(table)
        sys.stdout.write('\n')
    elif table_name == 'last':
        height = 1
        for i in range(height + add_height):
            sys.stdout.write("\033[F\033[K")
        sys.stdout.write(f"LAST ACTION: {globals.LAST_ACTION}\n")
    else:
        raise Exception("module does not exist")
    return height


def main():
    if json.loads(utils.read_file('config/setup.json'))["tle_update"]['update'] is True:
        interval = float(json.loads(utils.read_file('config/setup.json'))["tle_update"]['update_interval'])
        pre_sat_file = ast.literal_eval(utils.read_file('config/tle.json'))
        tle_update_manager_thread = threading.Thread(target=tle_manager.tle_update_manager,
                                                     args=(interval, pre_sat_file,))
        tle_update_manager_thread.start()

    heights = [['map', draw_board('map', first_time=True, add_height=0)],
               ['flyby', draw_board('flyby', first_time=True, add_height=0)],
               ['info', draw_board('info', first_time=True, add_height=0)],
               ['last', draw_board('last', first_time=True, add_height=0)]]

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
                for i in range(index+1, len(heights)):
                    add_height += heights[i][1]
                draw_board(key, first_time=False, add_height=add_height)
                for i in range(index+1, len(heights)):
                    draw_board(heights[i][0], first_time=True, add_height=0)
                timeouts[key] = timeouts_load[key]


if __name__ == '__main__':
    main()
