import requests
import time
import json
import ast

from satellites import satellite
import globals
import utils


def read_tle(sat_json):
    sats = []
    for key in sat_json:
        sats.append(satellite(key,
                              sat_json[key]["line1"],
                              sat_json[key]["line2"],
                              sat_json[key]["freq"],
                              sat_json[key]["type"]))
    return sats


def tle_update_manager(interval, sats):
    while True:
        for sat in sats:
            update_tle(str(sats[sat]['catalog_number']), str(sat))
        globals.LAST_ACTION = f"updated tle files from online source at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        globals.LOGGER.error(f"updated {len(sats)} tle files from online source")
        time.sleep(interval)


def update_tle(catnum, name):
    pre_sat_file = ast.literal_eval(utils.read_file('config/tle.json'))
    url = f'https://celestrak.com/NORAD/elements/gp.php?CATNR={catnum}&FORMAT=tle'
    r = requests.get(url)
    if r.status_code == 200:
        lines = r.text.split('\n')
        if len(lines[1]) == 70 and len(lines[2]) == 70:
            pre_sat_file[name]['line1'] = str(lines[1]).rstrip('\r').rstrip('\n')
            pre_sat_file[name]['line2'] = str(lines[2]).rstrip('\r').rstrip('\n')
            utils.write_file('config/tle.json', json.dumps(pre_sat_file, sort_keys=False, indent=4))
