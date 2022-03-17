import globals
import utils


def draw_box(drawing_settings):
    spaces = [100, 20]

    text_buffer = utils.add_col(f"LAST ACTION: {globals.LAST_ACTION}", spaces[0]) + \
                  utils.add_col(f"RADIO:", spaces[1])
    target = f"http://{globals.HOST}:{globals.PORT}"
    if drawing_settings.render == 'ansi':
        server = f"SERVER: \u001b]8;;{target}\u001b\\{target}\u001b]8;;\u001b\\"
    elif drawing_settings.render == 'html':
        server = f"SERVER: {target}"
    else:
        raise Exception(f"unsupported render type: {drawing_settings.render}")

    text_buffer += (' ' * (globals.WIDTH - len(text_buffer) - len(target) - len("SERVER:")) + server)

    if drawing_settings.render == 'ansi':
        return text_buffer, 1
    elif drawing_settings.render == 'html':
        table = "<pre>" + text_buffer + "</pre>"
        return table, 1
    else:
        raise Exception("unsupported render type")
