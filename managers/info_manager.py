import globals
import utils


def draw_box(satellites, drawing_settings):
    width = globals.WIDTH
    upper_left_corner = drawing_settings.option['upper_left_corner']
    upper_right_corner = drawing_settings.option['upper_right_corner']
    lower_right_corner = drawing_settings.option['lower_right_corner']
    lower_left_corner = drawing_settings.option['lower_left_corner']
    horizontal_line = drawing_settings.option['horizontal_line']
    vertical_line = drawing_settings.option['vertical_line']
    left_opener = drawing_settings.option['left_opener']
    right_opener = drawing_settings.option['right_opener']

    border_color = drawing_settings.option[drawing_settings.render]['border_color']
    text_color = drawing_settings.option[drawing_settings.render]['text_color']
    info_color = drawing_settings.option[drawing_settings.render]['info_color']
    end_color = drawing_settings.option[drawing_settings.render]['end_color']

    if drawing_settings.render == 'ansi':
        border_color = '\033' + border_color
        text_color = '\033' + text_color
        info_color = '\033' + info_color
        end_color = '\033' + end_color
    elif drawing_settings.render == 'html':
        border_color = '<span style="color:' + border_color + '">'
        text_color = '<span style="color:' + text_color + '">'
        info_color = '<span style="color:' + info_color + '">'
        end_color = '</span>'
    else:
        raise Exception("unsupported render type")

    table = ''

    name = f"{left_opener} SATELLITE INFO {right_opener}"
    half_len = int(len(name) / 2)
    left_side = int(width / 2) - half_len
    table += str(border_color + upper_left_corner + horizontal_line * left_side + name + horizontal_line * (width - (left_side + len(name))) + upper_right_corner + end_color + '\n')

    spaces = [1, 15, 15, 20, 8, 4, 8, 14, 12, 4, 15, 15, 15, 4, 10]

    text_buffer = utils.add_col("", spaces[0]) + \
                  utils.add_col("SATELLITE:", spaces[1]) + \
                  utils.add_col("EPOCH:", spaces[2]) + \
                  utils.add_col("FREQUENCY:", spaces[3]) + \
                  utils.add_col("TYPE:", spaces[4]) + \
                  utils.add_col(" ", spaces[5]) + \
                  utils.add_col("DIR:", spaces[6]) + \
                  utils.add_col("LAT:", spaces[7]) + \
                  utils.add_col("LON:", spaces[8]) + \
                  utils.add_col(" ", spaces[9]) + \
                  utils.add_col("ALTIDUDE:", spaces[10]) + \
                  utils.add_col("AZIMUTH:", spaces[11]) + \
                  utils.add_col("DISTANCE:", spaces[12]) + \
                  utils.add_col(" ", spaces[13]) + \
                  utils.add_col("DOPPLER:", spaces[14])

    text_buffer += ' ' * (width - len(text_buffer))

    table += str(border_color + vertical_line + info_color + text_buffer + border_color + vertical_line + end_color + '\n')

    for sat in satellites:
        line_data = sat.get_json()

        text_buffer = utils.add_col("", spaces[0]) + \
                      utils.add_col(line_data["name"], spaces[1]) + \
                      utils.add_col(str(float(line_data["epoch"]))[:4] + " days", spaces[2]) + \
                      utils.add_col(str("{:.5f}".format(line_data["freq"])) + " MHz", spaces[3]) + \
                      utils.add_col(line_data["type"], spaces[4]) + \
                      utils.add_col("|", spaces[5]) + \
                      utils.add_col(str("⟰" if line_data["direction"] == "up" else "⟱"), spaces[6]) + \
                      utils.add_col(str(float(line_data["position"]["lat"]))[:7] + "°", spaces[7]) + \
                      utils.add_col(str(float(line_data["position"]["lon"]))[:7] + "°", spaces[8]) + \
                      utils.add_col("|", spaces[9]) + \
                      utils.add_col(str(float(line_data["perspective"]["altitude"]))[:7] + "°", spaces[10]) + \
                      utils.add_col(str(float(line_data["perspective"]["azimuth"]))[:7] + "°", spaces[11]) + \
                      utils.add_col(str(float(line_data["perspective"]["distance"]))[:7] + "Km", spaces[12]) + \
                      utils.add_col("|", spaces[13]) + \
                      utils.add_col(str(float(line_data["doppler"]))[:7] + " Hz", spaces[14])

        text_buffer += ' ' * (width - len(text_buffer))

        table += str(border_color + vertical_line + text_color + text_buffer + border_color + vertical_line + end_color + '\n')

    table += str(border_color + lower_left_corner + horizontal_line * width + lower_right_corner + end_color + '\n\n')

    height = len(satellites) + 4

    return table, height
