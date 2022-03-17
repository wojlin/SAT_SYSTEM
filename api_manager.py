from werkzeug.exceptions import HTTPException
from flask import Flask, render_template, request
from datetime import datetime, timedelta
import logging
import click
import os
import ast

import globals
import utils
from managers import info_manager, flyby_manager, map_manager, tle_manager, decode_manager, logging_manager, status_manager

template_path = os.path.join(globals.PATH, 'templates')
static_path = os.path.join(globals.PATH, 'static')
app = Flask(__name__, template_folder=template_path, static_folder=static_path)
'''app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True
log.setLevel(logging.ERROR)
logging.getLogger('werkzeug').disabled = True'''


def secho(text, file=None, nl=None, err=None, color=None, **styles):
    pass


def echo(text, file=None, nl=None, err=None, color=None, **styles):
    pass


click.echo = echo
click.secho = secho

sat_file = ast.literal_eval(utils.read_file('config/tle.json'))
sats = tle_manager.read_tle(sat_file)

'''@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        globals.LOGGER.error(e)
        return e'''


@app.route("/api/get_map", methods=["GET"])
def get_map_box():
    options_keys = request.args
    options = globals.HTML_DRAWING_SETTINGS
    for key in options_keys:
        if options_keys[key] == "true":
            options.option["map_config"][key] = True
        elif options_keys[key] == "false":
            options.option["map_config"][key] = False
        else:
            options.option["map_config"][key] = options_keys[key]
    map_box = map_manager.draw_box(sats, options)
    return str(map_box[0])


@app.route("/api/get_flyby", methods=["GET"])
def get_flyby_box():
    options_keys = request.args
    options = globals.HTML_DRAWING_SETTINGS
    for key in options_keys:
        if options_keys[key] == "true":
            options.option["flyby_config"][key] = True
        elif options_keys[key] == "false":
            options.option["flyby_config"][key] = False
        else:
            options.option["flyby_config"][key] = options_keys[key]
    hours = int(options.option["flyby_config"]['hours_ahead'])
    angle = int(options.option["flyby_config"]['minimal_angle'])
    amount = int(options.option["flyby_config"]['display_amount'])
    filtered_list = flyby_manager.get_flyby_filtered_list(sats, datetime.utcnow(),
                                                          datetime.utcnow() + timedelta(hours=hours), angle)
    flyby_box = flyby_manager.draw_box(filtered_list, amount, drawing_settings=options)

    return str(flyby_box[0])


@app.route("/api/get_info", methods=["GET"])
def get_info_box():
    options = globals.HTML_DRAWING_SETTINGS
    info_box = info_manager.draw_box(sats, drawing_settings=options)

    return str(info_box[0])


@app.route("/api/get_status", methods=["GET"])
def get_status_box():
    options = globals.HTML_DRAWING_SETTINGS
    status_box = status_manager.draw_box(drawing_settings=options)
    return str(status_box[0])


@app.route("/")
def index():
    return render_template('index.html')


def start_api():
    try:
        app.run(globals.HOST, globals.PORT, False)
    except Exception as e:
        globals.LOGGER.error(e)


if __name__ == "__main__":
    app.run(globals.HOST, globals.PORT, True)
