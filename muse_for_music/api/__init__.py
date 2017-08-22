from flask import Blueprint
from flask_restplus import Api
from .. import app

api_blueprint = Blueprint('api', __name__)

api = Api(api_blueprint, version='0.1', title='MUSE4Music API', doc='/doc/',
          description='The reatful api for muse 4 music.')

from . import root, taxonomies, data


app.register_blueprint(api_blueprint, url_prefix='/api')
