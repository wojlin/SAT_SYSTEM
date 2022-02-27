import math
from datetime import datetime, timedelta
import globals

width = 180
height = 45


class earth_char:
    def __init__(self, left, center, right):
        self.left_side = left
        self.center = center
        self.right_side = right

    def merged(self):
        return str(self.left_side + self.center + self.right_side)

    def __repr__(self):
        return str(self.left_side + self.center + self.right_side)


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
                    y_raw_map[x] = earth_char(color, char, bcolors.ENDC)
                    if name != '':
                        for c in range(len(name)):
                            if 2 + x + c >= width:
                                i = width - (x + c)
                                y_raw_map[i] = earth_char(color, name[c], bcolors.ENDC)
                            else:
                                y_raw_map[2 + x + c] = earth_char(color, name[c], bcolors.ENDC)
                    if direction != '':
                        if direction == "⟰":
                            if y + 2 > 0:
                                y_arrow_raw_map = list(raw_map[y - 1])
                                y_arrow_raw_map[x] = earth_char(color, '⟰', bcolors.ENDC)
                                raw_map[y - 1] = y_arrow_raw_map
                        else:
                            if y + 2 < height:
                                y_arrow_raw_map = list(raw_map[y + 1])
                                y_arrow_raw_map[x] = earth_char(color, '⟱', bcolors.ENDC)
                                raw_map[y + 1] = y_arrow_raw_map
                        pass
                    raw_map[y] = y_raw_map
                lon += int(360 / width)
        lat += int(180 / height)
    return raw_map


def draw_box(satellites, pathes):

    sats_buffer = satellites

    top_left = "╔"
    top_right = "╗"
    bottom_right = "╝"
    bottom_left = "╚"
    horizontal = "═"
    vertical = "║"
    map = ''

    with open('config/cli_earth', 'r') as f:

        name = "╣ SATELLITE MAP ╠"
        half_len = int(len(name)/2)
        left_side = int(width/2) - half_len
        map += str(top_left + horizontal * left_side + name + horizontal * (width - (left_side + len(name))) + top_right + '\n')

        raw_map = []
        for line in f:
            raw_map.append([earth_char(bcolors.EARTH, char, bcolors.ENDC) for char in list(line.rstrip("\n"))])

        raw_map = draw_point(raw_map, globals.POS["lat"], globals.POS["lon"], "o", bcolors.HOME, name="HOME")

        colors = ['\033[1;33;40m', '\033[1;35;40m', '\033[1;36;40m', '\033[1;37;40m']
        current_color = 0
        for sat in sats_buffer:
            l_sat = sat.get_json()
            path_points = sat.get_position_path(datetime.utcnow(), datetime.utcnow() + timedelta(seconds=pathes), 60)
            for point in path_points:
                l_raw_map = draw_point(raw_map, path_points[point]["lat"], path_points[point]["lon"], "'", colors[current_color])
                raw_map = l_raw_map

            current_color += 1
            if current_color >= len(colors):
                current_color = 0
            raw_map = l_raw_map

        current_color = 0
        for sat in sats_buffer:
            l_sat = sat.get_json()
            l_raw_map = draw_point(raw_map, l_sat["position"]['lat'], l_sat["position"]['lon'], "🛰",
                                   colors[current_color],
                                   name=l_sat["name"], direction=str("⟰" if l_sat["direction"] == "up" else "⟱"))

            current_color += 1
            if current_color >= len(colors):
                current_color = 0
            raw_map = l_raw_map

        for line in raw_map:
            joined_raw_map = ''.join([point.merged() for point in line])
            map += str(
                bcolors.BORDER + vertical + bcolors.ENDC + joined_raw_map + bcolors.BORDER + vertical + bcolors.ENDC + "\n")
        map += str(bcolors.BORDER + bottom_left + horizontal * width + bottom_right + bcolors.ENDC + '\n')

    map_height = height + 2
    return map, map_height
