import globals
import utils
import json


def draw_box(drawing_settings):
    last_action = utils.add_col(f"LAST ACTION: {globals.LAST_ACTION}", 95)

    if json.loads(utils.read_file('config/setup.json'))["decode_settings"]['use_rotator'] is True:
        radio = utils.add_col(f"ROTATOR: ⟳ {str(globals.ROTATOR_AZIMUTH).zfill(2)}°  ∠ {str(globals.ROTATOR_ELEVATION).zfill(2)}°", 50)
    else:
        radio = utils.add_col("ROTATOR: disabled", 50)

    if json.loads(utils.read_file('config/setup.json'))["api_settings"]['use_api'] is True:
        target = f"http://{globals.API_HOST}:{globals.API_PORT}"
        if drawing_settings.render == 'ansi':
            server = f"SERVER: \u001b]8;;{target}\u001b\\{target}\u001b]8;;\u001b\\"
        elif drawing_settings.render == 'html':
            server = f"SERVER: {target}"
        else:
            raise Exception(f"unsupported render type: {drawing_settings.render}")
    else:
        server = "SERVER: disabled"

    text_buffer = last_action + radio + server

    if drawing_settings.render == 'ansi':
        return text_buffer, 1
    elif drawing_settings.render == 'html':
        table = "<pre>" + text_buffer + "</pre>"
        return table, 1
    else:
        raise Exception("unsupported render type")
