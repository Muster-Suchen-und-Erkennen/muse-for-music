"""Root Module for the API."""

from flask import Blueprint, Flask
from flask_restx import Api, abort
from flask_restx.errors import ValidationError
from flask_jwt_extended.exceptions import NoAuthorizationError

from ..user_api import log_unauthorized

api_blueprint = Blueprint('api', __name__)

authorizations = {
    'jwt': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Standard JWT access token from user Api.'
    },
}

api = Api(api_blueprint, version='0.1', title='MUSE4Music API', doc='/doc/',
          authorizations=authorizations, security='jwt',
          description='The restful api for muse 4 music.')

from . import root, taxonomies, data


@api.errorhandler(ValidationError)
def handle_validation_erorr(error: ValidationError):
    """Validation failed."""
    return {
        "errors": error.msg,
        "message": "Input payload validation failed"
    }


@api.errorhandler(NoAuthorizationError)
def missing_header(error):
    """User is not authorized for this operation."""
    log_unauthorized(str(error))
    return {'message': str(error)}, 401


def register_api(app: Flask):
    app.register_blueprint(api_blueprint, url_prefix='/api')
