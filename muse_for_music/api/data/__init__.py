"""Module containing API Endpoints for data Resources."""

from flask_restx import fields, Resource

from .. import api

from . import people
from . import opus
from . import part
from . import subpart

from . import history
