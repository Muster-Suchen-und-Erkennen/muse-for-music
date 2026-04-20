"""Root Module for the API."""

from http import HTTPStatus

from flask import Blueprint, Flask
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_restx import Api
from flask_restx.errors import ValidationError

from ..user_api import log_unauthorized

api_blueprint = Blueprint("api", __name__)

authorizations = {
    "jwt": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Standard JWT access token from user Api.",
    },
}

api = Api(
    version="0.1",
    title="MUSE4Music API",
    doc="/doc/",
    authorizations=authorizations,
    security="jwt",
    description="The restful api for muse 4 music.",
)

from . import data, root, taxonomies  # noqa

api.init_app(api_blueprint)


@api.errorhandler(ValidationError)
def handle_validation_erorr(error: ValidationError):
    """Validation failed."""
    return {
        "errors": error.msg,
        "message": "Input payload validation failed",
    }, HTTPStatus.BAD_REQUEST


@api.errorhandler(NoAuthorizationError)
def missing_header(error):
    """User is not authorized for this operation."""
    log_unauthorized(str(error))
    return {"message": str(error)}, HTTPStatus.UNAUTHORIZED


def register_api(app: Flask):
    app.register_blueprint(api_blueprint, url_prefix="/api")
