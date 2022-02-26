import utils


def draw_info(satellites):
    top_left = "╔"
    top_right = "╗"
    bottom_right = "╝"
    bottom_left = "╚"
    horizontal = "═"
    vertical = "║"

    table = ''
    width = 180

    name = "╣ SATELLITE INFO ╠"
    half_len = int(len(name) / 2)
    left_side = int(width / 2) - half_len
    table += str(top_left + horizontal * left_side + name + horizontal * (width - (left_side + len(name))) + top_right + '\n')

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

    table += str(vertical + text_buffer + vertical + '\n')

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

        table += str(vertical + text_buffer + vertical + '\n')

    table += str(bottom_left + horizontal * width + bottom_right + '\n\n')

    height = len(satellites) + 4

    return table, height
