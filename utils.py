from datetime import datetime
from dateutil import tz
import time


def add_col(input_str, space):
    if len(str(input_str)) > space:
        input_str = str(input_str)[:-(len(str(input_str)) - space) - 3] + "..."
    return str(str(input_str) + ' ' * (space - len(str(input_str)))) + ' '


def deg(degree):
    return str(round(float(degree), 2)) + "°"


def min_sec(time):
    minutes = int(time / 60)
    seconds = int(time - (minutes * 60))
    return f"{str(minutes).zfill(2)}m {str(seconds).zfill(2)}s"


def read_file(_path):
    try:
        with open(_path, 'r') as _file:
            return _file.read()
    except Exception as e:
        raise Exception(e)


def write_file(_path, text):
    try:
        with open(_path, 'w') as _file:
            _file.write(text)
            _file.close()
    except Exception as e:
        raise Exception(e)


def get_utc_offset():
    offset = -time.timezone
    mark = ''
    if offset > 0:
        mark = '+'
    return f"{mark}{int(offset/3600)}"


def utc_to_lc(utc_time):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S')
    utc = utc.replace(tzinfo=from_zone)

    central = utc.astimezone(to_zone).strftime('%Y-%m-%d %H:%M:%S')

    return central
