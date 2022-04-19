import time
from datetime import datetime, timedelta
from PIL import Image
import numpy as np
import math

import globals

width = globals.WIDTH
height = globals.HEIGHT


class earth_char:
    """
    class that contain information about what is left side of char, char, right side of char
    """

    def __init__(self, left, center, right):
        self.left_side = left
        self.center = center
        self.right_side = right

    def merged(self):
        return str(self.left_side + self.center + self.right_side)

    def __repr__(self):
        return str(self.left_side + self.center + self.right_side)


def draw_point(drawing_settings: globals.options, raw_map: list, position: tuple, char: str, color: str, **kwargs):
    """
    this function creates point on map. It's capable of drawing name, direction and custom symbol as well
    :param drawing_settings: class options that contain information on how to draw map
    :param raw_map: list that contain map
    :param position: tuple of y and x coordinates
    :param char: char that will be displayed at that point
    :param color: color of symbol, can be hex or ansi
    :param kwargs: other parmeters like name of point or direction
    :return: raw_map with new point drawn on it
    """
    global height, width

    if drawing_settings.render == 'ansi':  # checking what draw mode was selected
        end_color = '\033' + drawing_settings.option[drawing_settings.render]['end_color']
    elif drawing_settings.render == 'html':
        end_color = '</span>'
    else:
        raise Exception("unsupported render type")

    name = ''
    direction = ''

    for arg in kwargs:  # checking additional options
        if arg == "name":
            name = kwargs[arg]
        if arg == "direction":
            direction = kwargs[arg]

    lat = position[0]
    lon = position[1]

    rescale_x = lambda x: ((x * 360) / width) - 180
    rescale_y = lambda y: ((y * 180) / height) - 90
    x_loc = next((x for x in range(1, width + 1) if (rescale_x(x) <= lon <= rescale_x(x + 1))), 0)
    y_loc = height - next((y for y in range(1, height + 1) if (rescale_y(y) <= lat <= rescale_y(y + 1))), 0)

    y_raw_map = list(raw_map[y_loc])
    y_raw_map[x_loc] = earth_char(color, char, end_color)

    """ drawing name """
    if name != '':
        space = 0
        for character in range(len(name)):
            if 2 + x_loc + character >= width:  # start from left if name is outside bounds
                y_raw_map[space] = earth_char(color, name[character], end_color)
                space += 1
            else:
                y_raw_map[2 + x_loc + character] = earth_char(color, name[character], end_color)

    """ drawing direction arrow """
    if direction != '':
        arrow_up = drawing_settings.option["chars"]['arrow_up']
        arrow_down = drawing_settings.option["chars"]['arrow_down']
        if direction == "up":
            if y_loc + 2 > 0:
                y_arrow_raw_map = list(raw_map[y_loc - 1])
                y_arrow_raw_map[x_loc] = earth_char(color, arrow_up, end_color)
                raw_map[y_loc - 1] = y_arrow_raw_map
        else:
            if y_loc + 2 < height:
                y_arrow_raw_map = list(raw_map[y_loc + 1])
                y_arrow_raw_map[x_loc] = earth_char(color, arrow_down, end_color)
                raw_map[y_loc + 1] = y_arrow_raw_map

    raw_map[y_loc] = y_raw_map

    return raw_map


def terminator(_width: int, date: datetime):
    """
    this function is used to create map showing where on earth is day and where is night
    :param _width: 
    :param date: current date object input
    :return: 2d matrix of point where zero represents night and one represents day
    """

    """
    The solar altitude angle measured at noon will differ from the corresponding
    equinoctial angle by an angle of up to ± 23° 17'. This angle is called the solar declination.
    It is defined as the angular distance from the zenith of the observer at the equator and the sun at solar noon.
    It is positive when it is north and negative when it is south. The declination reaches its maximum value, +23° 17',
    on 21 June (the summer solstice in the northern hemisphere, the winter solstice in the southern hemisphere).
    The minimum value, −23° 27', is reached on 20 December. The declination, in degrees,
    for any given day may be calculated in first approximation with the equation:
    δ=(23+27/60)sin((360*d/365.25)deg)
    where d is number of day in year
    """

    declination = (23 + 27 / 60) * math.sin(((360 * date.timetuple().tm_yday) / 365.25) * (np.pi / 180))

    """
    our angle, in astronomy, the angle between an observer’s meridian
    (a great circle passing over his head and through the celestial poles) and the hour circle
    (any other great circle passing through the poles) on which some celestial body lies.
    This angle, when expressed in hours and minutes, is the time elapsed since the celestial body’s last transit
    of the observer’s meridian. The hour angle can also be expressed in degrees, 15° of arc being equal to one hour.
    """

    hour_angle = 360 * (date.hour / 24)

    twilight_degree = -25  # bias because sunset does not mean that its dark outside

    """
    the magic that creates the map of the day and night 
    (I don't understand how it works but it works so I guess it's okay)
    """

    _height = int(((_width - 1) / 2) + 1)
    dg2rad = np.pi / 180.
    n_lon = np.linspace(-180, 180, _width)
    longitude = n_lon + hour_angle
    lats = np.arctan(-np.cos(longitude * dg2rad) / np.tan(declination * dg2rad)) / dg2rad

    n_lon_2 = np.linspace(-180, 180, _width)
    n_lat_2 = np.linspace(-90, 90, _height)
    n_lon_2, n_lat_2 = np.meshgrid(n_lon_2, n_lat_2)

    if declination > 0:
        day_night = np.zeros(n_lon_2.shape, np.int)
        for _width in range(_width):
            day_night[:, _width] = np.where(n_lat_2[:, _width] < lats[_width] + twilight_degree, 1,
                                            day_night[:, _width])
    else:
        day_night = np.ones(n_lon_2.shape, np.int)
        for _width in range(_width):
            day_night[:, _width] = np.where(n_lat_2[:, _width] < lats[_width] + twilight_degree, 0,
                                            day_night[:, _width])

    return day_night


def earth_map(drawing_settings: globals.options):
    global width, height
    earth_land = drawing_settings.option["chars"]['earth_land']
    earth_ocean = drawing_settings.option["chars"]['earth_ocean']

    img = Image.open('static/images/earth.png')
    scaler = (width / (float(img.size[0] * 2)))
    hsize = int((float(img.size[1]) * float(scaler)))
    img = img.resize((width, hsize), Image.ANTIALIAS)
    img = img.convert('1')
    pixels = img.load()
    w, h = img.size
    all_pixels = [[0 for x in range(w)] for y in range(h)]
    for y in range(h):
        for x in range(w):
            all_pixels[y][x] = earth_ocean if pixels[x, y] == 0 else earth_land
    height = len(all_pixels)
    return all_pixels


def draw_box(satellites: list, drawing_settings: globals.options):
    """
    this function draws the map using the drawing settings and list of sattelites
    :param satellites: list that contains satellite classes
    :param drawing_settings: class options that contains drawing settings
    :return: string with map drawn on it
    """

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
    border_color = drawing_settings.option[drawing_settings.render]['border_color']
    earth_color = drawing_settings.option[drawing_settings.render]['earth_color']
    earth_color_night = drawing_settings.option[drawing_settings.render]['earth_color_night']
    earth_color_sunset = drawing_settings.option[drawing_settings.render]['earth_color_sunset']
    end_color = drawing_settings.option[drawing_settings.render]['end_color']
    ground_station_color = drawing_settings.option[drawing_settings.render]['ground_station_color']

    """changing the content of variables depending on the drawing mode"""
    if drawing_settings.render == 'ansi':
        border_color = '\033' + border_color
        earth_color = '\033' + earth_color
        earth_color_night = '\033' + earth_color_night
        earth_color_sunset = '\033' + earth_color_sunset
        end_color = '\033' + end_color
        sat_colors = ['\033' + color for color in drawing_settings.option[drawing_settings.render]['sat_colors']]
        ground_station_color = '\033' + ground_station_color
    elif drawing_settings.render == 'html':
        border_color = '<span style="color:' + border_color + '">'
        earth_color = '<span style="color:' + earth_color + '">'
        earth_color_night = '<span style="color:' + earth_color_night + '">'
        earth_color_sunset = '<span style="color:' + earth_color_sunset + '">'
        end_color = '</span>'
        sat_colors = ['<span style="color:' + color + '">' for color in
                      drawing_settings.option[drawing_settings.render]['sat_colors']]
        ground_station_color = '<span style="color:' + ground_station_color + '">'
    else:
        raise Exception("unsupported render type")

    """drawing map"""
    sats_buffer = satellites
    table = ''

    char_map = earth_map(drawing_settings)

    name = f"{left_opener} satellite map {right_opener}"
    half_len = int(len(name) / 2)
    left_side = int(width / 2) - half_len
    table += str(border_color + upper_left_corner + str(horizontal_line * left_side) + str(name) + str(
        horizontal_line * (width - (left_side + len(name)))) + upper_right_corner + end_color + '\n')

    raw_map = []

    for line in char_map:
        raw_map.append([earth_char(earth_color, char, end_color) for char in list(line)])

    if drawing_settings.option["map_config"]['draw_day_night_cycle'] is True:
        night_day = terminator(width, datetime.now())

        for y in range(len(raw_map)):
            for x in range(len(raw_map[y])):
                if int(night_day[y][x]) == 0:
                    raw_map[y][x].left_side = earth_color_night

        for y in range(len(raw_map)):
            for x in range(len(raw_map[y]) - 1):
                if int(night_day[y][x]) == 0 and int(night_day[y][x + 1]) == 1:
                    raw_map[y][x].left_side = earth_color_sunset
                    raw_map[y][x].center = sunset

        for y in range(len(raw_map)):
            for x in range(len(raw_map[y]) - 1):
                if int(night_day[y][x]) == 1 and int(night_day[y][x + 1]) == 0:
                    raw_map[y][x].left_side = earth_color_sunset
                    raw_map[y][x].center = sunset

    if drawing_settings.option["map_config"]['draw_ground_station']:
        raw_map = draw_point(drawing_settings, raw_map, (globals.POS["lat"], globals.POS["lon"]), ground_station,
                             ground_station_color,
                             name=ground_station_name)

    colors = sat_colors
    current_color = 0

    if drawing_settings.option["map_config"]['draw_satellite_path'] is True:
        for sat in sats_buffer:
            resolution = int(drawing_settings.option["map_config"]['satellite_path_resolution'])
            ahead = int(drawing_settings.option["map_config"]['satellite_path_time_ahead'])
            path_points = sat.get_position_path(datetime.utcnow(), datetime.utcnow() + timedelta(seconds=ahead),
                                                resolution)
            l_raw_map = []
            for point in path_points:
                l_raw_map = draw_point(drawing_settings, raw_map, (path_points[point]["lat"],
                                                                   path_points[point]["lon"]), "'",
                                       colors[current_color])
                raw_map = l_raw_map

            current_color += 1
            if current_color >= len(colors):
                current_color = 0
            raw_map = l_raw_map

    current_color = 0

    for sat in sats_buffer:
        l_sat = sat.get_json()
        l_raw_map = draw_point(drawing_settings, raw_map, (l_sat["position"]['lat'], l_sat["position"]['lon']),
                               satellite,
                               colors[current_color],
                               name=l_sat["name"],
                               direction=l_sat["direction"])

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

    if drawing_settings.render == 'ansi':
        return table, map_height
    elif drawing_settings.render == 'html':
        table = "<pre>" + table + "</pre>"
        return table, map_height
    else:
        raise Exception("unsupported render type")
