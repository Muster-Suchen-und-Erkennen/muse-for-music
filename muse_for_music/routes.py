from flask import render_template, url_for
from flask_cors import CORS, cross_origin

from . import app

from . import user_api
from . import api


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           title='muse4music')
    #return render_template('test.html',
    #                       css=url_for('static', filename='test.css'),
    #                       name='test')
