from werkzeug.exceptions import HTTPException
from os import listdir
from os.path import isfile, join
from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime, timedelta
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import logging
from io import BytesIO
import click
import os
import ast

import globals
import utils
from managers import info_manager, flyby_manager, map_manager, tle_manager, decode_manager, logging_manager, \
    status_manager

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
    map_box = map_manager.draw_box(sats, options,
                                   width=int(options.option["map_config"]['width']),
                                   padding=globals.PADDING)
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
    flyby_box = flyby_manager.draw_box(filtered_list, amount,
                                       drawing_settings=options,
                                       width=int(options.option["flyby_config"]['width']),
                                       padding=globals.PADDING)

    return str(flyby_box[0])


@app.route("/api/get_info", methods=["GET"])
def get_info_box():
    options = globals.HTML_DRAWING_SETTINGS
    options_keys = request.args
    info_box = info_manager.draw_box(sats,
                                     drawing_settings=options,
                                     width=int(options_keys['width']),
                                     padding=globals.PADDING)

    return str(info_box[0])


@app.route("/api/get_status", methods=["GET"])
def get_status_box():
    options = globals.HTML_DRAWING_SETTINGS
    options_keys = request.args
    status_box = status_manager.draw_box(drawing_settings=options,
                                         width=int(options_keys['width']),
                                         padding=globals.PADDING)
    return str(status_box[0])


@app.route("/api/get_images_list", methods=["GET"])
def get_images_list():
    options_keys = request.args

    path = globals.OUTPUT
    files = [f for f in listdir(path) if isfile(join(path, f))]
    sorted_files = sorted(files, key=lambda x: str(x), reverse=True)[:int(options_keys["show_x_first"])]
    return_json = {}
    for f in range(len(sorted_files)):
        return_json[f] = {"filename": sorted_files[f],
                          "date": ' '.join(str(sorted_files[f]).split(' ')[:2]),
                          "sat_name": ' '.join(str(sorted_files[f]).split(' ')[2:]).split('.')[0]}
    return jsonify(return_json)


@app.route("/api/get_image_thumbnail", methods=["GET"])
def get_image_thumbnail():
    path = globals.OUTPUT
    options_keys = request.args

    filename = options_keys['name']
    img = Image.open(os.path.join(path, filename))
    img = img.convert('RGB')
    width, height = img.size
    img = img.resize((width // 10, height // 10))

    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


@app.route("/api/get_image", methods=["GET"])
def get_image():
    path = globals.OUTPUT
    options_keys = request.args

    filename = options_keys['name']
    img = Image.open(os.path.join(path, filename))
    img = img.convert('RGB')
    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


@app.route("/api/get_image_metadata", methods=["GET"])
def get_image_metadata():
    path = globals.OUTPUT
    options_keys = request.args

    filename = options_keys['name']
    img = Image.open(os.path.join(path, filename))
    #json_obj = ast.literal_eval(img.text["sat_data"])
    #print(json_obj)
    return str(img.text["sat_data"])


@app.route("/")
def index():
    return render_template('index.html', host=globals.API_HOST, port=globals.API_PORT)


def start_api():
    try:
        app.run(globals.API_HOST, globals.API_PORT, False)
    except Exception as e:
        globals.LOGGER.error(e)
