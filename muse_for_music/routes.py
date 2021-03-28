from flask import Flask, render_template, url_for, redirect, abort
from flask_cors import CORS, cross_origin

from .user_api import register_user_api
from .api import register_api


def register_routes(app: Flask, flask_static_digest):

    register_user_api(app)
    register_api(app)

    if app.config['DEBUG']:
        from .debug_routes import register_debug_routes
        register_debug_routes(app)


    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def index(path: str):
        if path.startswith('/api/') or path.startswith('/user-api/'):
            abort(404)
        return render_template('index.html', title='muse4music')


    @app.route('/<string:file>')
    def static_resources(file):
        if '.' in file:
            return redirect(flask_static_digest.static_url_for('static', filename=file))
        return render_template('index.html', title='muse4music')


    @app.route('/assets/<string:file>')
    def asset(file):
        if '.' in file:
            return redirect(flask_static_digest.static_url_for('static', filename='assets/' + file))
        return render_template('index.html', title='muse4music')
