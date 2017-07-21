from flask import Blueprint, render_template
from .. import app

debug_blueprint = Blueprint('debug_routes', __name__, template_folder='templates')

from . import debug_taxonomies


@debug_blueprint.route('/')
@debug_blueprint.route('/index')
def index():
    return render_template('debug/index.html',
                           title='muse4music – Debug')


app.register_blueprint(debug_blueprint, url_prefix='/debug')
