from datetime import datetime, timedelta
import json
import ast

import utlis
from satellites import satellite
import term_earth


def read_tle(sat_json):
    sats = []
    for key in sat_json:
        sats.append(satellite(key,
                              sat_json[key]["line1"],
                              sat_json[key]["line2"],
                              sat_json[key]["freq"],
                              sat_json[key]["type"]))
    return sats


def main():
    sat_file = ast.literal_eval(utlis.read_file('config/tle.json'))
    sats = read_tle(sat_file)

    for sat in sats:
        pass
        #print(json.dumps(ast.literal_eval(str(sat)), indent=4))
        #print(json.dumps(sat.get_passes(datetime.utcnow(), datetime.utcnow() + timedelta(hours=13), 15), indent=4))
        #print(sat.get_perspective_path(datetime.utcnow(), datetime.utcnow() + timedelta(hours=3), 50))
        #print(sat.get_position_path(datetime.utcnow(), datetime.utcnow() + timedelta(hours=3), 50))
        #print()

    term_earth.draw_map(satellites=sats, pathes=3600)


if __name__ == '__main__':
    main()
