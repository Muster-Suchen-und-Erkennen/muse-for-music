from flask import Blueprint
from flask_restplus import Api
from .. import app

api_blueprint = Blueprint('api', __name__)

api = Api(api_blueprint, version='0.1', title='My Test API', doc='/doc',
          description='A simple test of a Flask RestPlus powered API')

from .endpoints.test import ns as endpoint_test

#api.init_app(api_blueprint)
api.add_namespace(endpoint_test)


app.register_blueprint(api_blueprint, url_prefix='/api')
