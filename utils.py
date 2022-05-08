from functools import reduce
from datetime import datetime
from dateutil import tz
import time
import json
import ast


class Table:
    def __init__(self, name: str, width: int, height: int, padding: int, columns: dict, rows: dict, drawing_settings):

        self.drawing_settings = drawing_settings

        self.upper_left_corner = self.drawing_settings.option["chars"]['upper_left_corner']
        self.upper_right_corner = self.drawing_settings.option["chars"]['upper_right_corner']
        self.lower_right_corner = self.drawing_settings.option["chars"]['lower_right_corner']
        self.lower_left_corner = self.drawing_settings.option["chars"]['lower_left_corner']
        self.horizontal_line = self.drawing_settings.option["chars"]['horizontal_line']
        self.vertical_line = self.drawing_settings.option["chars"]['vertical_line']
        self.left_opener = self.drawing_settings.option["chars"]['left_opener']
        self.right_opener = self.drawing_settings.option["chars"]['right_opener']
        self.border_color = self.drawing_settings.option[self.drawing_settings.render]['border_color']
        self.text_color = self.drawing_settings.option[self.drawing_settings.render]['text_color']
        self.info_color = self.drawing_settings.option[self.drawing_settings.render]['info_color']
        self.end_color = self.drawing_settings.option[self.drawing_settings.render]['end_color']

        if self.drawing_settings.render == 'ansi':
            self.border_color = '\033' + self.border_color
            self.text_color = '\033' + self.text_color
            self.info_color = '\033' + self.info_color
            self.end_color = '\033' + self.end_color
        elif self.drawing_settings.render == 'html':
            self.border_color = '<span style="color:' + self.border_color + '">'
            self.text_color = '<span style="color:' + self.text_color + '">'
            self.info_color = '<span style="color:' + self.info_color + '">'
            self.end_color = '</span>'
        else:
            raise Exception("unsupported render type")

        for key, values in rows.items():
            if len(values) != len(columns):
                raise Exception(f"table cannot be crated because amount of columns ({len(values)}) in row {key} does "
                                f"not match size of table ({len(columns)}) ")
        self.padding = padding
        self.width = width - (self.padding * 2) - 2
        self.columns = columns
        self.rows = rows
        self.name = name
        self.height = height

    @staticmethod
    def add_cell(text: str, width: int):
        text_len = len(text)
        if text_len > width:
            text = text[:-(text_len - width) - 3] + "..."
        return str(text).ljust(width)

    def start_table(self):
        name = f"{self.left_opener} {self.name} {self.right_opener}"
        half_len = int(len(name) / 2)
        left_side = int(self.width / 2) - half_len
        lines_left = str(self.horizontal_line) * left_side
        lines_right = str(self.horizontal_line) * (self.width - (left_side + len(name)))
        return self.fill_table(lines_left + name + lines_right, row_type='top')

    def end_table(self):
        return self.fill_table(str(self.horizontal_line) * self.width, row_type='bottom')

    def fill_table(self, text: str, heading: bool = False, row_type: str = "content"):
        if self.drawing_settings.render == 'html':
            padding = "<span>" + str(" " * self.padding) + "</span>"
        else:
            padding = " " * self.padding
        if row_type == "content":
            left = self.vertical_line
            right = self.vertical_line
            color = self.info_color if heading else self.text_color
        elif row_type == "top":
            left = self.upper_left_corner
            right = self.upper_right_corner
            color = self.border_color
        elif row_type == "bottom":
            left = self.lower_left_corner
            right = self.lower_right_corner
            color = self.border_color
        else:
            raise Exception(f"unsupported row type: {row_type}\nsupported types: ['content', 'top', 'bottom']")
        line_start = str(padding + self.border_color + left + self.end_color + color)
        line_end = str(self.end_color + self.border_color + right + self.end_color + padding + '\n')
        return line_start + text + line_end

    @staticmethod
    def extend_table(width, lines):
        left_width = width
        current_line = 0
        max_line = len(lines)
        while left_width > 0:
            lines[current_line] += ' '
            current_line += 1
            if current_line == max_line:
                current_line = 0
            left_width -= 1

        return ''.join(lines)

    def format_table(self):
        lines = [[self.add_cell(cell['name'], cell['width']) for key, cell in self.columns.items()]]

        for key, rows in self.rows.items():
            lines.append([self.add_cell(rows[cell], self.columns[cell]['width']) for cell in range(len(rows))])

        return lines

    def shrink_row(self, row: list):
        lowest_priority = max([cell['priority'] for key, cell in self.columns.items()])
        cols = self.columns.copy()
        row_len = len(''.join(row))
        new_row = row
        new_col = cols
        while row_len > self.width:
            temp_row = []
            temp_col = []
            for i, cell in enumerate(new_row):
                if new_col[i]['priority'] < lowest_priority:
                    temp_row.append(cell)
                    temp_col.append(cols[i])
            lowest_priority -= 1
            row_len = len(''.join(new_row))
            new_row = temp_row
            new_col = temp_col
        return new_row

    def draw(self):
        table = ''

        table += self.start_table()
        lines = self.format_table()

        amount = self.height + 1
        head = True
        for row in lines:

            total_len = sum([len(line) for line in row])
            left_width = self.width - total_len
            if amount > 0:
                if left_width > 0:
                    table += self.fill_table(self.extend_table(left_width, row), heading=head)
                else:
                    new_row = self.shrink_row(row)
                    total_len = sum([len(line) for line in new_row])
                    new_left_width = self.width - total_len
                    table += self.fill_table(self.extend_table(new_left_width, new_row), heading=head)
            head = False
            amount -= 1

        table += self.end_table()

        if self.drawing_settings.render == 'ansi':
            return table
        elif self.drawing_settings.render == 'html':
            table = f"<pre id='{self.name}'>" + table + "</pre>"
            return table
        else:
            raise Exception("unsupported render type")

    def __repr__(self):
        return self.draw()


def read_config(path):
    setup = json.loads(read_file('config/setup.json'))
    return reduce(dict.get, path, setup)


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
    """
    this function generates a stamp with information on how far local time is from utc time
    :return: string with timestamp
    """
    offset = -(datetime.utcnow().hour - datetime.now().hour)
    mark = ''
    if offset > 0:
        mark = '+'
    return f"{mark}{int(offset)}"


def utc_to_lc(utc_time):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S')
    utc = utc.replace(tzinfo=from_zone)

    central = utc.astimezone(to_zone).strftime('%Y-%m-%d %H:%M:%S')

    return central
