import utils
import globals


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


def draw_box(flyby_json, entries_amount):
    width = globals.WIDTH
    upper_left_corner = globals.DRAWING_SETTINGS['upper_left_corner']
    upper_right_corner = globals.DRAWING_SETTINGS['upper_right_corner']
    lower_right_corner = globals.DRAWING_SETTINGS['lower_right_corner']
    lower_left_corner = globals.DRAWING_SETTINGS['lower_left_corner']
    horizontal_line = globals.DRAWING_SETTINGS['horizontal_line']
    vertical_line = globals.DRAWING_SETTINGS['vertical_line']
    left_opener = globals.DRAWING_SETTINGS['left_opener']
    right_opener = globals.DRAWING_SETTINGS['right_opener']
    border_color = '\033' + globals.DRAWING_SETTINGS['border_color']
    text_color = '\033' + globals.DRAWING_SETTINGS['text_color']
    info_color = '\033' + globals.DRAWING_SETTINGS['info_color']
    end_color = '\033' + globals.DRAWING_SETTINGS['end_color']

    table = ''

    start = float(flyby_json["settings"]['start_epoch'])
    end = float(flyby_json["settings"]['end_epoch'])
    min_degree = flyby_json["settings"]['min_degree']
    hours = int((end - start) / 3600)
    name = f"{left_opener} FLYBY INFO (min {min_degree}° altitude, {hours} hours ahead, showing first {entries_amount}, UTC {utils.get_utc_offset()}) {right_opener}"
    half_len = int(len(name) / 2)
    left_side = int(width / 2) - half_len
    table += str(
        border_color + upper_left_corner + horizontal_line * left_side + name + horizontal_line * (
                width - (left_side + len(name))) + upper_right_corner + end_color + '\n')

    entry = 0

    spaces = [6, 15, 12, 12, 2, 22, 10, 5, 2, 22, 10, 5, 2, 22, 10, 5]

    text_buffer = utils.add_col(" NO:", spaces[0]) + \
                  utils.add_col("SATELLITE:", spaces[1]) + \
                  utils.add_col("MAX ALT:", spaces[2]) + \
                  utils.add_col("DURATION:", spaces[3]) + \
                  utils.add_col("|", spaces[4]) + \
                  utils.add_col("RISE:", spaces[5]) + \
                  utils.add_col("AZIMUTH:", spaces[6]) + \
                  utils.add_col("DIR:", spaces[7]) + \
                  utils.add_col("|", spaces[8]) + \
                  utils.add_col("CULMINATE:", spaces[9]) + \
                  utils.add_col("AZIMUTH:", spaces[10]) + \
                  utils.add_col("DIR:", spaces[11]) + \
                  utils.add_col("|", spaces[12]) + \
                  utils.add_col("SET:", spaces[13]) + \
                  utils.add_col("AZIMUTH:", spaces[14]) + \
                  utils.add_col("DIR:", spaces[15])

    text_buffer += ' ' * (width - len(text_buffer))

    table += str(border_color + vertical_line + info_color + text_buffer + end_color + border_color + vertical_line + '\n')

    for key in flyby_json["events"]:
        entry += 1
        if entry <= entries_amount:
            rise_time = utils.utc_to_lc(flyby_json["events"][key]["rise"]['time'])
            culminate_time = utils.utc_to_lc(flyby_json["events"][key]["culminate"]['time'])
            set_time = utils.utc_to_lc(flyby_json["events"][key]["set"]['time'])

            text_buffer = utils.add_col(f" {str(entry).zfill(2)}.", spaces[0]) + \
                          utils.add_col(flyby_json["events"][key]["name"], spaces[1]) + \
                          utils.add_col(str(round(float(flyby_json["events"][key]["culminate"]['altitude']), 2)) + "°",
                                        spaces[2]) + \
                          utils.add_col(utils.min_sec(float(flyby_json["events"][key]["duration"])), spaces[3]) + \
                          utils.add_col("|", spaces[4]) + \
                          utils.add_col(rise_time, spaces[5]) + \
                          utils.add_col(utils.deg(flyby_json["events"][key]["rise"]['azimuth']), spaces[6]) + \
                          utils.add_col(flyby_json["events"][key]["rise"]['direction'], spaces[7]) + \
                          utils.add_col("|", spaces[8]) + \
                          utils.add_col(culminate_time, spaces[9]) + \
                          utils.add_col(utils.deg(flyby_json["events"][key]["culminate"]['azimuth']), spaces[10]) + \
                          utils.add_col(flyby_json["events"][key]["culminate"]['direction'], spaces[11]) + \
                          utils.add_col("|", spaces[12]) + \
                          utils.add_col(set_time, spaces[13]) + \
                          utils.add_col(utils.deg(flyby_json["events"][key]["set"]['azimuth']), spaces[14]) + \
                          utils.add_col(flyby_json["events"][key]["set"]['direction'], spaces[15])

            text_buffer += ' ' * (width - len(text_buffer))

            table += border_color + vertical_line + text_color + text_buffer + end_color + border_color + vertical_line + '\n'

    for x in range(entries_amount - entry):
        entry += 1
        table += vertical_line + f" {str(entry).zfill(2)}. " + ' ' * (width - 5) + vertical_line + '\n'

    table += lower_left_corner + horizontal_line * width + lower_right_corner + '\n'

    height = entries_amount + 4
    return table, height
