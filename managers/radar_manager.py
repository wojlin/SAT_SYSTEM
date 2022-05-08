import datetime
import math
import json
import time

from managers import flyby_manager
import satellites
import utils


class PolarPoint:
    def __init__(self, name: str, coordinate: tuple, width: int, padding: tuple):
        self.name = name
        self.azimuth = coordinate[0]
        self.angle = coordinate[1]
        self.width = width
        self.radius = math.floor(self.width / 2)
        self.padding = padding

    def calculate(self):
        distance = self.radius - ((self.angle / 90) * self.radius)
        angle = math.radians(self.azimuth - 90)
        y = distance * math.sin(angle)
        x = distance * math.cos(angle)
        x = int(x + self.padding[0] + self.radius)
        y_rescale = 2.2
        y = int((y + self.radius) / y_rescale) + self.padding[1]
        return x, y

    def draw(self):
        x, y = self.calculate()
        table = f"\033[{y};{x}H{self.name}"
        return table


class Circle:
    def __init__(self, circle_radius: int, rescale: float, padding: tuple, points_amount: int, color: str, char: str):
        self.radius = circle_radius
        self.padding_x = padding[0]
        self.padding_y = padding[1]
        self.points_amount = points_amount
        self.color = color
        self.char = char
        self.rescale = rescale

    def draw(self):
        table = ''
        pi = math.pi
        y_rescale = 2.2

        x = [int((math.sin((x / self.points_amount) * 2 * pi) * (self.radius * self.rescale)) + self.radius + self.padding_x) for x in
             range(self.points_amount)]
        y = [int(((math.cos(
            (y / self.points_amount) * 2 * pi) * (self.radius * self.rescale)) + self.radius) / y_rescale) + self.padding_y for y in
             range(self.points_amount)]
        for i in range(self.points_amount):
            table += f"\033[{y[i]};{x[i]}H{self.color}{self.char}"

        return table


def draw_box(sats: list[satellites], padding: tuple, width: int, drawing_settings):
    """defining shorter name for options parameters"""
    upper_left_corner = drawing_settings.option["chars"]['upper_left_corner']
    upper_right_corner = drawing_settings.option["chars"]['upper_right_corner']
    lower_right_corner = drawing_settings.option["chars"]['lower_right_corner']
    lower_left_corner = drawing_settings.option["chars"]['lower_left_corner']
    horizontal_line = drawing_settings.option["chars"]['horizontal_line']
    vertical_line = drawing_settings.option["chars"]['vertical_line']
    left_opener = drawing_settings.option["chars"]['left_opener']
    right_opener = drawing_settings.option["chars"]['right_opener']
    satellite = drawing_settings.option["chars"]['satellite']
    ground_station = drawing_settings.option["chars"]['ground_station']
    ground_station_name = drawing_settings.option["chars"]['ground_station_name']
    sunset = drawing_settings.option["chars"]['sunset']
    satellite = drawing_settings.option["chars"]['satellite']
    border_color = drawing_settings.option[drawing_settings.render]['border_color']
    earth_color = drawing_settings.option[drawing_settings.render]['earth_color']
    radar_color = drawing_settings.option[drawing_settings.render]['radar_color']
    earth_color_night = drawing_settings.option[drawing_settings.render]['earth_color_night']
    earth_color_sunset = drawing_settings.option[drawing_settings.render]['earth_color_sunset']
    end_color = drawing_settings.option[drawing_settings.render]['end_color']
    text_color = drawing_settings.option[drawing_settings.render]['text_color']
    ground_station_color = drawing_settings.option[drawing_settings.render]['ground_station_color']

    """changing the content of variables depending on the drawing mode"""
    if drawing_settings.render == 'ansi':
        border_color = '\033' + border_color
        earth_color = '\033' + earth_color
        radar_color = '\033' + radar_color
        earth_color_night = '\033' + earth_color_night
        earth_color_sunset = '\033' + earth_color_sunset
        end_color = '\033' + end_color
        text_color = '\033' + text_color
        sat_colors = ['\033' + color for color in drawing_settings.option[drawing_settings.render]['sat_colors']]
        ground_station_color = '\033' + ground_station_color
    elif drawing_settings.render == 'html':
        border_color = '<span style="color:' + border_color + '">'
        earth_color = '<span style="color:' + earth_color + '">'
        radar_color = '<span style="color:' + radar_color + '">'
        earth_color_night = '<span style="color:' + earth_color_night + '">'
        earth_color_sunset = '<span style="color:' + earth_color_sunset + '">'
        end_color = '</span>'
        text_color = '<span style="color:' + text_color + '">'
        sat_colors = ['<span style="color:' + color + '">' for color in
                      drawing_settings.option[drawing_settings.render]['sat_colors']]
        ground_station_color = '<span style="color:' + ground_station_color + '">'
    else:
        raise Exception("unsupported render type")

    y_rescale = 2.2
    radar_width = width - 10
    radar_height = int(radar_width / y_rescale)
    radius = math.floor(radar_width / 2)
    points = int(radar_width * 1.5)
    x_padding = padding[0]
    y_padding = padding[1]
    radar_x_padding = padding[0] + 6
    radar_y_padding = y_padding + 5
    table_y_padding = 5

    total_height = (radar_y_padding - y_padding) + radar_height + table_y_padding + len(sats) + 2

    table = ''

    name = f"{left_opener} radar {right_opener}"
    half_len = int(len(name) / 2)
    left_side = int(width / 2) - half_len
    table += f"\033[{y_padding};{x_padding}H" + str(
        border_color + upper_left_corner + str(horizontal_line * left_side) + str(name) + str(
            horizontal_line * (width - (
                    left_side + len(name)))) + upper_right_corner + end_color)

    for i in range(1, total_height):
        table += f"\033[{y_padding + i};{x_padding}H{border_color}{vertical_line}{radar_color}{' ' * (width)}{border_color}{vertical_line}{end_color}"

    table += f"\033[{y_padding + total_height};{x_padding}H{border_color}{lower_left_corner}{horizontal_line * width}{lower_right_corner}{end_color}"

    table += Circle(radius, 1, (radar_x_padding, radar_y_padding), points, radar_color, '.').draw()
    table += Circle(radius, 0.70, (radar_x_padding, radar_y_padding), int(points/2), radar_color, '.').draw()
    table += Circle(radius, 0.35, (radar_x_padding, radar_y_padding), int(points/3), radar_color, '.').draw()

    table += f"\033[{radar_y_padding - 1};{radius + radar_x_padding}H0°"
    table += f"\033[{int(radius / y_rescale) + radar_y_padding};{radar_width + radar_x_padding}H90°"
    table += f"\033[{int(radius / y_rescale) + radar_y_padding};{radar_x_padding - 4}H270°"
    table += f"\033[{int((radar_width / y_rescale) + radar_y_padding) + 1};{radius + radar_x_padding - 1}H180°"

    for i in range(radar_width - 2):
        table += f"\033[{int(radius / y_rescale) + radar_y_padding};{i + radar_x_padding + 1}H{radar_color}-"

    for i in range(radar_width - 2):
        table += f"\033[{int(i / y_rescale) + radar_y_padding + 1};{radius + radar_x_padding}H{radar_color}¦"

    table += f"\033[{int(radius / y_rescale) + radar_y_padding + 1};{int(radius + (radius - radius * 1) + radar_x_padding + 1)}H90°"
    table += f"\033[{int(radius / y_rescale) + radar_y_padding + 1};{int(radius + (radius - radius * 0.65) + radar_x_padding + 1)}H60°"
    table += f"\033[{int(radius / y_rescale) + radar_y_padding + 1};{int(radius + (radius - radius * 0.3) + radar_x_padding + 1)}H30°"

    colors = sat_colors
    current_color = 0

    sats_colors = {}

    l_name = f" legend "
    l_half_len = int(len(name) / 2)
    l_left_side = int(width / 2) - l_half_len
    table += f"\033[{radar_y_padding + radar_height + table_y_padding - 1};{x_padding + 2}H{radar_color}" + str(
        str('-' * l_left_side) + str(l_name) + str('-' * (width - 1 - (l_left_side + len(name)))))

    for i in range(len(sats)):
        sat_json = sats[i].get_json()
        name = sat_json["name"]
        color = colors[current_color]
        sats_colors[name] = colors[current_color]
        table += f"\033[{int(radar_width / y_rescale) + radar_y_padding + table_y_padding + 1 + i};{radar_x_padding}H{end_color}{color}███{end_color}{radar_color} - {str(name).ljust(radar_width - 9)}"
        current_color += 1
        if current_color >= len(colors):
            current_color = 0

    table += f"\033[{40 + radar_y_padding};0H"

    hours = int(int(json.loads(utils.read_file('config/setup.json'))["drawing_settings"]["map_config"][
                        'satellite_path_time_ahead']) / 3600)
    angle = int(
        json.loads(utils.read_file('config/setup.json'))["drawing_settings"]["flyby_config"]['minimal_angle'])

    flyby_list = flyby_manager.get_flyby_raw_list(sats, datetime.datetime.utcnow() - datetime.timedelta(minutes=10),
                                                  datetime.datetime.utcnow() + datetime.timedelta(hours=hours),
                                                  angle)

    paths = {}

    for key, val in flyby_list['events'].items():
        name = val['name']
        rise_time = datetime.datetime.strptime(val['rise']['time'], '%Y-%m-%d %H:%M:%S')
        set_time = datetime.datetime.strptime(val['set']['time'], '%Y-%m-%d %H:%M:%S')
        for i in range(len(sats)):
            if sats[i].name == name:
                path = sats[i].get_perspective_path(rise_time, set_time, 50)
                paths[name] = path

    for sat, points in paths.items():
        for index, point in points.items():
            p = PolarPoint(f"{sats_colors[sat]}•{end_color}", (point['azimuth'], point['altitude']), radar_width,
                           (radar_x_padding, radar_y_padding))
            table += p.draw()

    for sat in sats:
        sat_info = sat.get_json()
        if sat_info['perspective']['altitude'] > 0:
            p = PolarPoint(f"{radar_color}{sats_colors[sat_info['name']]}{satellite} {sat_info['name']}",
                           (sat_info['perspective']['azimuth'], sat_info['perspective']['altitude']), radar_width,
                           (radar_x_padding, radar_y_padding))
            table += p.draw()
    table += end_color
    return table, 0
