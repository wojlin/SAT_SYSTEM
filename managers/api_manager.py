from werkzeug.exceptions import HTTPException
from flask import Flask, render_template, request
import logging
import click
import os
import ast

import globals
import utils
from managers import info_manager, flyby_manager, map_manager, tle_manager, decode_manager, logging_manager

template_path = os.path.join(globals.PATH, 'templates')
static_path = os.path.join(globals.PATH, 'static')
app = Flask(__name__, template_folder=template_path, static_folder=static_path)
app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True
log.setLevel(logging.ERROR)
logging.getLogger('werkzeug').disabled = True


def secho(text, file=None, nl=None, err=None, color=None, **styles):
    pass


def echo(text, file=None, nl=None, err=None, color=None, **styles):
    pass


click.echo = echo
click.secho = secho

sat_file = ast.literal_eval(utils.read_file('config/tle.json'))
sats = tle_manager.read_tle(sat_file)


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        globals.LOGGER.error(e)
        return e


@app.route("/api/get_map", methods=["POST"])
def get_map_box():
    options_keys = request.args
    for key in options_keys:
        print(key)
    options = globals.HTML_DRAWING_SETTINGS
    map_box = map_manager.draw_box(sats, options)
    return map_box


@app.route("/")
def index():
    return render_template('index.html')


def start_api():
    try:
        app.run(globals.HOST, globals.PORT, False)
    except Exception as e:
        globals.LOGGER.error(e)


if __name__ == "__main__":
    start_api()