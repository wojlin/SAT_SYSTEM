import globals
import utils


def draw_box(satellites, drawing_settings, width, padding):

    _columns = {0: {"name": " SATELLITE:", "priority": 0, "width": 15},
                1: {"name": "EPOCH:", "priority": 3, "width": 11},
                2: {"name": "FREQUENCY:", "priority": 4, "width": 13},
                3: {"name": "TYPE:", "priority": 4, "width": 9},
                4: {"name": "|", "priority": 0, "width": 1},
                5: {"name": "DIR:", "priority": 2, "width": 5},
                6: {"name": "LAT:", "priority": 1, "width": 13},
                7: {"name": "LON:", "priority": 1, "width": 13},
                8: {"name": "|", "priority": 0, "width": 1},
                9: {"name": "ALTIDUDE:", "priority": 0, "width": 13},
                10: {"name": "AZIMUTH:", "priority": 0, "width": 13},
                11: {"name": "DISTANCE:", "priority": 2, "width": 13},
                12: {"name": "|", "priority": 5, "width": 2},
                13: {"name": "DOPPLER:", "priority": 5, "width": 12},
                }

    _rows = {}

    i = 0
    for sat in satellites:
        line_data = sat.get_json()

        _rows[i] = [f" {line_data['name']}",
                    str(float(line_data["epoch"]))[:4] + " days",
                    str("{:.5f}".format(line_data["freq"])) + " MHz",
                    line_data["type"],
                    "|",
                    str("⟰" if line_data["direction"] == "up" else "⟱"),
                    str(float(line_data["position"]["lat"]))[:7] + "°",
                    str(float(line_data["position"]["lon"]))[:7] + "°",
                    "|",
                    str(float(line_data["perspective"]["altitude"]))[:7] + "°",
                    str(float(line_data["perspective"]["azimuth"]))[:7] + "°",
                    str(float(line_data["perspective"]["distance"]))[:7] + "Km",
                    "|",
                    str(float(line_data["doppler"]))[:7] + " Hz"]

        i += 1

    height = i + 4
    table = utils.Table("SATELLITE INFO", width, len(satellites), padding, _columns, _rows, drawing_settings)
    return table.draw(), height
