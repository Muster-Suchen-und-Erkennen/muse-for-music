"""Module containing the root resource of the API."""

from flask_restx import marshal

from . import user_api
from .models import root_model


def render_root_custom():
    return marshal(None, root_model)


user_api.render_root = render_root_custom  # type: ignore
