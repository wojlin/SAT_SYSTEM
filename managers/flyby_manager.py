import utils


def get_flyby_raw_list(sats, t_in, t_out, degree):
    template = {"settings": {
        "start_epoch": t_in.timestamp(),
        "end_epoch": t_out.timestamp(),
        "start_utc": t_in.strftime('%Y-%m-%d %H:%M:%S'),
        "end_utc": t_out.strftime('%Y-%m-%d %H:%M:%S'),
        "min_degree": degree
    }}

    flyby_list = [sat.get_passes(t_in, t_out, degree) for sat in sats]
    flat_list = {}
    for list_dict in flyby_list:
        for event in list_dict['events']:
            flat_list[event] = (list_dict['events'][event])
    sorted_list = {k: v for k, v in sorted(flat_list.items(), key=lambda item: item)}
    sorted_list = {**template, **{"events": sorted_list}}
    return sorted_list


def get_flyby_filtered_list(sats, t_in, t_out, degree):
    template = {"settings": {
        "start_epoch": t_in.timestamp(),
        "end_epoch": t_out.timestamp(),
        "start_utc": t_in.strftime('%Y-%m-%d %H:%M:%S'),
        "end_utc": t_out.strftime('%Y-%m-%d %H:%M:%S'),
        "min_degree": degree
    }}

    flyby_raw_dict = get_flyby_raw_list(sats, t_in, t_out, degree)

    flyby_raw_list = []
    for key in flyby_raw_dict["events"]:
        flyby_raw_dict["events"][key]["draw"] = True
        flyby_raw_dict["events"][key]["epoch"] = key
        flyby_raw_list.append(dict(flyby_raw_dict["events"][key]))

    for key in range(len(flyby_raw_list) - 1):
        if float(flyby_raw_list[key]["set"]["epoch"]) > float(flyby_raw_list[key + 1]["rise"]["epoch"]):
            if float(flyby_raw_list[key]["culminate"]["altitude"]) < float(
                    flyby_raw_list[key + 1]["culminate"]["altitude"]):
                flyby_raw_list[key]["draw"] = False
            else:
                flyby_raw_list[key + 1]["draw"] = False

    filtered_list = {}
    for key in flyby_raw_list:
        if key["draw"] == True:
            key.pop('draw', None)
            epoch = key["epoch"]
            filtered_list[epoch] = key

    return {**template, **{"events": filtered_list}}


def draw_box(flyby_json, entries_amount, drawing_settings, width, padding):

    _columns = {0: {"name": " NO:", "priority": 0, "width": 4},
                1: {"name": "SATELLITE:", "priority": 0, "width": 11},
                2: {"name": "MAX ALT:", "priority": 0, "width": 8},
                3: {"name": "DURATION:", "priority": 0, "width": 9},
                4: {"name": "|", "priority": 2, "width": 2},
                5: {"name": "RISE:", "priority": 1, "width": 22},
                6: {"name": "AZIMUTH:", "priority": 3, "width": 10},
                7: {"name": "DIR:", "priority": 4, "width": 4},
                8: {"name": "|", "priority": 3, "width": 2},
                9: {"name": "CULMINATE:", "priority": 3, "width": 22},
                10: {"name": "AZIMUTH:", "priority": 3, "width": 10},
                11: {"name": "DIR:", "priority": 4, "width": 4},
                12: {"name": "|", "priority": 2, "width": 2},
                13: {"name": "SET:", "priority": 1, "width": 22},
                14: {"name": "AZIMUTH:", "priority": 3, "width": 10},
                15: {"name": "DIR:", "priority": 4, "width": 4},
                }

    _rows = {}

    entry = 0
    for key in flyby_json["events"]:
        entry += 1
        if entry <= entries_amount:
            rise_time = utils.utc_to_lc(flyby_json["events"][key]["rise"]['time'])
            culminate_time = utils.utc_to_lc(flyby_json["events"][key]["culminate"]['time'])
            set_time = utils.utc_to_lc(flyby_json["events"][key]["set"]['time'])

            _rows[entry] = [f" {str(entry).zfill(2)}.",
                            str(flyby_json["events"][key]["name"]),
                            str(round(float(flyby_json["events"][key]["culminate"]['altitude']), 2)) + "°",
                            str(utils.min_sec(float(flyby_json["events"][key]["duration"]))),
                            "|",
                            str(rise_time),
                            str(utils.deg(flyby_json["events"][key]["rise"]['azimuth'])),
                            str(flyby_json["events"][key]["rise"]['direction']),
                            "|",
                            str(culminate_time),
                            str(utils.deg(flyby_json["events"][key]["culminate"]['azimuth'])),
                            str(flyby_json["events"][key]["culminate"]['direction']),
                            "|",
                            str(set_time),
                            str(utils.deg(flyby_json["events"][key]["set"]['azimuth'])),
                            str(flyby_json["events"][key]["set"]['direction'])]

    height = entries_amount + 2

    start = float(flyby_json["settings"]['start_epoch'])
    end = float(flyby_json["settings"]['end_epoch'])
    min_degree = flyby_json["settings"]['min_degree']
    hours = int((end - start) / 3600)
    name = f"FLYBY INFO (min {min_degree}° altitude, {hours} hours ahead, showing first {entries_amount}, UTC {utils.get_utc_offset()})"
    table = utils.Table(name, width, entries_amount, padding, _columns, _rows, drawing_settings)
    return table.draw(), height + 2