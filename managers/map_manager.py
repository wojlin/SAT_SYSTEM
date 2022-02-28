import math
from datetime import datetime, timedelta

import globals

width = globals.WIDTH
height = globals.HEIGHT
upper_left_corner = globals.DRAWING_SETTINGS['upper_left_corner']
upper_right_corner = globals.DRAWING_SETTINGS['upper_right_corner']
lower_right_corner = globals.DRAWING_SETTINGS['lower_right_corner']
lower_left_corner = globals.DRAWING_SETTINGS['lower_left_corner']
horizontal_line = globals.DRAWING_SETTINGS['horizontal_line']
vertical_line = globals.DRAWING_SETTINGS['vertical_line']
left_opener = globals.DRAWING_SETTINGS['left_opener']
right_opener = globals.DRAWING_SETTINGS['right_opener']
satellite = globals.DRAWING_SETTINGS['satellite']
arrow_up = globals.DRAWING_SETTINGS['arrow_up']
arrow_down = globals.DRAWING_SETTINGS['arrow_down']
ground_station = globals.DRAWING_SETTINGS['ground_station']
ground_station_name = globals.DRAWING_SETTINGS['ground_station_name']
ground_station_color = '\033' + globals.DRAWING_SETTINGS['ground_station_color']
sat_colors = ['\033' + color for color in globals.DRAWING_SETTINGS['sat_colors']]
border_color = '\033' + globals.DRAWING_SETTINGS['border_color']
text_color = '\033' + globals.DRAWING_SETTINGS['text_color']
info_color = '\033' + globals.DRAWING_SETTINGS['info_color']
earth_color = '\033' + globals.DRAWING_SETTINGS['earth_color']
end_color = '\033' + globals.DRAWING_SETTINGS['end_color']


class earth_char:
    def __init__(self, left, center, right):
        self.left_side = left
        self.center = center
        self.right_side = right

    def merged(self):
        return str(self.left_side + self.center + self.right_side)

    def __repr__(self):
        return str(self.left_side + self.center + self.right_side)


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
                    y_raw_map[x] = earth_char(color, char, end_color)
                    if name != '':
                        for c in range(len(name)):
                            if 2 + x + c >= width:
                                i = width - (x + c)
                                y_raw_map[i] = earth_char(color, name[c], end_color)
                            else:
                                y_raw_map[2 + x + c] = earth_char(color, name[c], end_color)
                    if direction != '':
                        if direction == "⟰":
                            if y + 2 > 0:
                                y_arrow_raw_map = list(raw_map[y - 1])
                                y_arrow_raw_map[x] = earth_char(color, '⟰', end_color)
                                raw_map[y - 1] = y_arrow_raw_map
                        else:
                            if y + 2 < height:
                                y_arrow_raw_map = list(raw_map[y + 1])
                                y_arrow_raw_map[x] = earth_char(color, '⟱', end_color)
                                raw_map[y + 1] = y_arrow_raw_map
                        pass
                    raw_map[y] = y_raw_map
                lon += int(360 / width)
        lat += int(180 / height)
    return raw_map


def draw_box(satellites, pathes):
    sats_buffer = satellites

    table = ''

    with open('config/cli_earth', 'r') as f:

        name = f"{left_opener} satellite map {right_opener}"
        half_len = int(len(name) / 2)
        left_side = int(width / 2) - half_len
        table += str(border_color + upper_left_corner + str(horizontal_line * left_side) + str(name) + str(
            horizontal_line * (width - (left_side + len(name)))) + upper_right_corner + end_color + '\n')

        raw_map = []
        for line in f:
            raw_map.append([earth_char(earth_color, char, end_color) for char in list(line.rstrip("\n"))])

        raw_map = draw_point(raw_map, globals.POS["lat"], globals.POS["lon"], ground_station, ground_station_color,
                             name=ground_station_name)

        colors = sat_colors
        current_color = 0
        for sat in sats_buffer:
            path_points = sat.get_position_path(datetime.utcnow(), datetime.utcnow() + timedelta(seconds=pathes), 60)
            for point in path_points:
                l_raw_map = draw_point(raw_map, path_points[point]["lat"], path_points[point]["lon"], "'",
                                       colors[current_color])
                raw_map = l_raw_map

            current_color += 1
            if current_color >= len(colors):
                current_color = 0
            raw_map = l_raw_map

        current_color = 0
        for sat in sats_buffer:
            l_sat = sat.get_json()
            l_raw_map = draw_point(raw_map, l_sat["position"]['lat'], l_sat["position"]['lon'], satellite,
                                   colors[current_color],
                                   name=l_sat["name"],
                                   direction=str(arrow_up if l_sat["direction"] == "up" else arrow_down))

            current_color += 1
            if current_color >= len(colors):
                current_color = 0
            raw_map = l_raw_map

        for line in raw_map:
            joined_raw_map = ''.join([point.merged() for point in line])
            table += str(
                border_color + vertical_line + end_color + joined_raw_map + border_color + vertical_line + end_color + "\n")
        table += str(border_color) + str(lower_left_corner) + str(horizontal_line * width) + str(
            lower_right_corner + end_color + '\n')

    map_height = height + 2
    return table, map_height