from flask import render_template, url_for, send_from_directory
from flask_cors import CORS, cross_origin

from . import app

from . import user_api
from . import api

if app.config['DEBUG']:
    from . import debug_routes


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           title='muse4music')


@app.route('/assets/<path:file>')
def asset(file):
    return send_from_directory('./build', file)
