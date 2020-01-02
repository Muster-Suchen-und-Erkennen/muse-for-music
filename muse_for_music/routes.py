from flask import Flask, render_template, url_for, send_from_directory
from flask_cors import CORS, cross_origin

from .user_api import register_user_api
from .api import register_api


def register_routes(app: Flask):

    register_user_api(app)
    register_api(app)

    if app.config['DEBUG']:
        from .debug_routes import register_debug_routes
        register_debug_routes(app)


    @app.route('/')
    @app.route('/index')
    def index():
        return render_template('index.html',
                            title='muse4music')


    @app.route('/assets/<path:file>')
    def asset(file):
        return send_from_directory('./build', file)
