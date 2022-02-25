import math
from datetime import datetime, timedelta
import globals

width = 180
height = 45


class bcolors:
    BORDER = '\033[0m'
    HOME = '\033[1;31;40m'
    SAT = '\033[1;33;40m'
    EARTH = '\033[1;32;40m'
    ENDC = '\033[0m'


def draw_point(raw_map, lat_point, lon_point, char, color, **kwargs):
    global height, width
    lon = 0
    lat = 0
    name = ''
    direction = ''
    for arg in kwargs:
        if arg == "name":
            name = kwargs[arg]
        if arg == "direction":
            direction = kwargs[arg]

    for y in range(len(raw_map)):
        if 90 - lat <= math.floor(float(lat_point)) <= 90 - lat + int(180 / height):
            for x in range(width):
                if -180 + lon <= math.floor(float(lon_point)) <= -180 + lon + int(180 / width):
                    y_raw_map = list(raw_map[y])
                    y_raw_map[x] = f"{color}{char}{bcolors.ENDC}{bcolors.EARTH}"
                    if name != '':
                        for c in range(len(name)):
                            if 2+x+c >= width:
                                i = width - (x+c)
                                y_raw_map[i] = f"{color}{name[c]}{bcolors.ENDC}{bcolors.EARTH}"
                            else:
                                y_raw_map[2+x+c] = f"{color}{name[c]}{bcolors.ENDC}{bcolors.EARTH}"
                    if direction != '':
                        if direction == "⟰":
                            y_arrow_raw_map = list(raw_map[y-1])
                            y_arrow_raw_map[x] = f"{color}⟰{bcolors.ENDC}{bcolors.EARTH}"
                            raw_map[y-1] = ''.join(y_arrow_raw_map)
                        else:
                            y_arrow_raw_map = list(raw_map[y + 1])
                            y_arrow_raw_map[x] = f"{color}⟱{bcolors.ENDC}{bcolors.EARTH}"
                            raw_map[y + 1] = ''.join(y_arrow_raw_map)
                        pass
                    raw_map[y] = ''.join(y_raw_map)
                lon += int(360 / width)
        lat += int(180 / height)
    return raw_map


def draw_map(satellites, pathes):
    def add_col(input_str, space):
        if len(str(input_str)) > space:
            input_str = str(input_str)[:-(len(str(input_str)) - space) - 3] + "..."
        return str(str(input_str) + ' ' * (space - len(str(input_str)))) + ' '

    sats_buffer = satellites

    top_left = "╔"
    top_right = "╗"
    bottom_right = "╝"
    bottom_left = "╚"
    horizontal = "═"
    vertical = "║"
    inter_left = "╠"
    inter_right = "╣"
    map = ''

    with open('config/cli_earth', 'r') as f:
        map += str(bcolors.BORDER + top_left + horizontal * width + top_right + bcolors.ENDC + '\n')

        spaces = [1, 15, 15, 20, 8, 4, 8, 14, 12, 4, 15, 15, 15, 4, 10]

        text_buffer = add_col("", spaces[0]) + \
                      add_col("SATELLITE:", spaces[1]) + \
                      add_col("EPOCH:", spaces[2]) + \
                      add_col("FREQUENCY:", spaces[3]) + \
                      add_col("TYPE:", spaces[4]) + \
                      add_col(" ", spaces[5]) + \
                      add_col("DIR:", spaces[6]) + \
                      add_col("LAT:", spaces[7]) + \
                      add_col("LON:", spaces[8]) + \
                      add_col(" ", spaces[9]) + \
                      add_col("ALTIDUDE:", spaces[10]) + \
                      add_col("AZIMUTH:", spaces[11]) + \
                      add_col("DISTANCE:", spaces[12]) + \
                      add_col(" ", spaces[13]) + \
                      add_col("DOPPLER:", spaces[14])

        text_buffer += ' ' * (width - len(text_buffer))

        map += str(str(bcolors.BORDER + vertical + bcolors.ENDC) + text_buffer + str(
            bcolors.BORDER + vertical + bcolors.ENDC) + '\n')

        for sat in sats_buffer:
            line_data = sat.get_json()

            text_buffer = add_col("", spaces[0]) + \
                          add_col(line_data["name"], spaces[1]) + \
                          add_col(str(float(line_data["epoch"]))[:4] + " days", spaces[2]) + \
                          add_col(str("{:.5f}".format(line_data["freq"])) + " MHz", spaces[3]) + \
                          add_col(line_data["type"], spaces[4]) + \
                          add_col("|", spaces[5]) + \
                          add_col(str("⟰" if line_data["direction"] == "up" else "⟱"), spaces[6]) + \
                          add_col(str(float(line_data["position"]["lat"]))[:7] + "°", spaces[7]) + \
                          add_col(str(float(line_data["position"]["lon"]))[:7] + "°", spaces[8]) + \
                          add_col("|", spaces[9]) + \
                          add_col(str(float(line_data["perspective"]["altitude"]))[:7] + "°", spaces[10]) + \
                          add_col(str(float(line_data["perspective"]["azimuth"]))[:7] + "°", spaces[11]) + \
                          add_col(str(float(line_data["perspective"]["distance"]))[:7] + "Km", spaces[12]) + \
                          add_col("|", spaces[13]) + \
                          add_col(str(float(line_data["doppler"]))[:7] + " Hz", spaces[14])

            text_buffer += ' ' * (width - len(text_buffer))

            map += str(str(bcolors.BORDER + vertical + bcolors.ENDC) + text_buffer + str(
                bcolors.BORDER + vertical + bcolors.ENDC) + '\n')

        map += str(bcolors.BORDER + inter_left + horizontal * width + inter_right + bcolors.ENDC + '\n')

        raw_map = []
        for line in f:
            local_map = line.rstrip("\n")
            raw_map.append(local_map)

        raw_map = draw_point(raw_map, globals.POS["lat"], globals.POS["lon"], "#", bcolors.HOME, name="HOME")

        for sat in sats_buffer:
            l_sat = sat.get_json()
            path_points = sat.get_position_path(datetime.utcnow(), datetime.utcnow() + timedelta(seconds=pathes), 50)
            '''for point in path_points:
                l_raw_map = draw_point(raw_map, path_points[point]["lat"], path_points[point]["lon"], "*", bcolors.SAT)
                raw_map = l_raw_map'''

            l_raw_map = draw_point(raw_map, l_sat["position"]['lat'], l_sat["position"]['lon'], "@", bcolors.SAT, name=l_sat["name"], direction=str("⟰" if l_sat["direction"] == "up" else "⟱"))
            raw_map = l_raw_map

        for line in raw_map:
            map += str(
                bcolors.BORDER + vertical + bcolors.ENDC + bcolors.EARTH + line + bcolors.ENDC + bcolors.BORDER + vertical + bcolors.ENDC + "\n")
        map += str(bcolors.BORDER + bottom_left + horizontal * width + bottom_right + bcolors.ENDC + '\n')

    print(map)
