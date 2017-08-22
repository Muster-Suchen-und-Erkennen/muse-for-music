from logging import Formatter, Logger, DEBUG
from logging.handlers import RotatingFileHandler
from os import path
from functools import wraps
from typing import List
from flask import Blueprint, logging
from flask_restplus import Api, abort
from flask_jwt_extended import get_jwt_claims
from flask_jwt_extended.exceptions import NoAuthorizationError
from .. import app, jwt
from ..models.users import User, UserRole


authorizations = {
    'jwt': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Standard JWT access token.'
    },
    'jwt-refresh': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'JWT refresh token.'
    }
}


def has_roles(roles: List[UserRole]):
    """
    Check if the requesting user has one of the given roles.

    Must be applied after jwt_required decorator!
    """
    def has_roles_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            claims = get_jwt_claims()
            for role in roles:
                if role.name in claims:
                    break
            else:
                auth_logger.debug('Access to ressource with isufficient rights. User roles: %s, required roles: %s',
                                  [role.name for role in roles], claims)
                abort(403, 'Only members of the group(s) {} have access to this resource.'.format(
                    ', '.join([role.name for role in roles])
                ))
            return f(*args, **kwargs)
        return wrapper
    return has_roles_decorator


auth_logger = logging.create_logger(app)  # type: Logger

formatter = Formatter(fmt=app.config['AUTH_LOG_FORMAT'])

fh = RotatingFileHandler(path.join(app.config['LOG_PATH'], 'muse4music_auth.log'),
                         maxBytes=104857600, backupCount=10)

fh.setFormatter(formatter)

fh.setLevel(DEBUG)

auth_logger.addHandler(fh)


user_api_blueprint = Blueprint('user_api', __name__)

user_api = Api(user_api_blueprint, version='0.1', title='User API', doc='/doc/',
               authorizations=authorizations, security='jwt',
               description='API for Authentication and User Management.')


@jwt.user_identity_loader
def load_user_identity(user: User):
    return user.username


@jwt.user_claims_loader
def load_user_claims(user: User):
    return user.roles_json


@jwt.expired_token_loader
def expired_token():
    message = 'Token is expired.'
    log_unauthorized(message)
    abort(401, message)


@jwt.invalid_token_loader
def invalid_token(message: str):
    log_unauthorized(message)
    abort(401, message)


@jwt.unauthorized_loader
def unauthorized(message: str):
    log_unauthorized(message)
    abort(401, message)


@jwt.needs_fresh_token_loader
def stale_token():
    message = 'The JWT Token is not fresh. Please request a new Token directly with the /auth resource.'
    log_unauthorized(message)
    abort(403, message)


@jwt.revoked_token_loader
def revoked_token():
    message = 'The Token has been revoked.'
    log_unauthorized(message)
    abort(401, message)


@user_api.errorhandler(NoAuthorizationError)
def missing_header(error):
    log_unauthorized(error.message)
    return {'message': error.message}, 401


def log_unauthorized(message):
    auth_logger.debug('Unauthorized access: %s', message)


from .authentication import ns as authentication_endpoint
from .administration import ns as administration_endpoint


user_api.add_namespace(authentication_endpoint)
user_api.add_namespace(administration_endpoint)


app.register_blueprint(user_api_blueprint, url_prefix='/users')


