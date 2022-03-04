from werkzeug.exceptions import HTTPException
from flask import Flask, render_template
import logging
import click
import os

import globals

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


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        globals.LOGGER.error(e)
        return e


@app.route("/")
def index():
    return render_template('index.html')


def start_api():
    try:
        app.run(globals.HOST, globals.PORT, False)
    except Exception as e:
        globals.LOGGER.error(e)
