import globals
import utils
import math
import json


def draw_box(drawing_settings, width, padding):
    remain = width - 2 - (padding * 2)



    if json.loads(utils.read_file('config/setup.json'))["decode_settings"]['use_rotator'] is True:
        radio = f"ROTATOR: ⟳ {str(globals.ROTATOR_AZIMUTH).zfill(2)}°  ∠ {str(globals.ROTATOR_ELEVATION).zfill(2)}°".ljust(40)
    else:
        radio = utils.add_col("ROTATOR: disabled", math.floor(remain/4))

    if json.loads(utils.read_file('config/setup.json'))["api_settings"]['use_api'] is True:
        target = f"http://{globals.API_HOST}:{globals.API_PORT}"
        if drawing_settings.render == 'ansi':
            server = f"API: \u001b]8;;{target}\u001b\\{target}\u001b]8;;\u001b\\"
        elif drawing_settings.render == 'html':
            server = f"API: {target}"
        else:
            raise Exception(f"unsupported render type: {drawing_settings.render}")
    else:
        server = "SERVER: disabled"

    if width < 130:
        last_action = utils.add_col(f"LAST ACTION: {globals.LAST_ACTION}", math.floor(remain))
        text_buffer = (' ' * padding) + last_action
    elif width < 160:
        last_action = utils.add_col(f"LAST ACTION: {globals.LAST_ACTION}", math.floor(remain / 1.3))
        text_buffer = (' ' * padding) + last_action + radio
    else:
        last_action = utils.add_col(f"LAST ACTION: {globals.LAST_ACTION}", math.floor(remain / 2))
        text_buffer = (' ' * padding) + last_action + radio + server

    if drawing_settings.render == 'ansi':
        return text_buffer, 1
    elif drawing_settings.render == 'html':
        table = "<pre>" + text_buffer + "</pre>"
        return table, 1
    else:
        raise Exception("unsupported render type")
