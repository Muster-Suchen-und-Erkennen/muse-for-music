from flask import Flask, render_template, redirect, abort, Blueprint, Response
from flask.globals import g
from secrets import token_urlsafe

from .user_api import register_user_api
from .api import register_api

UI_BP = Blueprint("ui_blueprint", __name__, url_prefix="/")


@UI_BP.before_request
def before_requests():
    nonce = getattr(g, 'nonce', '')
    if not nonce:
        g.nonce = token_urlsafe(32)


@UI_BP.after_request
def inject_csp_headers(response: Response):
    nonce = getattr(g, 'nonce', '')
    script_nonce = f"'nonce-{nonce}'" if nonce else ""
    response.headers["Content-Security-Policy"] = f"default-src 'self'; script-src {script_nonce} 'self'; style-src 'self' 'unsafe-inline'"
    return response


def register_routes(app: Flask, flask_static_digest):

    register_user_api(app)
    register_api(app)

    if app.config['DEBUG']:
        from .debug_routes import register_debug_routes
        register_debug_routes(app)


    @UI_BP.route('/', defaults={'path': ''})
    @UI_BP.route('/<path:path>')
    def index(path: str):
        if path.startswith('/api/') or path.startswith('/user-api/'):
            abort(404)
        print(g.nonce)
        return render_template('index.html', title='muse4music', nonce=getattr(g, 'nonce', ''))


    @UI_BP.route('/<string:file>')
    def static_resources(file):
        if '.' in file:
            return redirect(flask_static_digest.static_url_for('static', filename=file))
        return render_template('index.html', title='muse4music', nonce=getattr(g, 'nonce', ''))


    @UI_BP.route('/assets/<string:file>')
    def asset(file):
        if '.' in file:
            return redirect(flask_static_digest.static_url_for('static', filename='assets/' + file))
        return render_template('index.html', title='muse4music', nonce=getattr(g, 'nonce', ''))

    app.register_blueprint(UI_BP)
