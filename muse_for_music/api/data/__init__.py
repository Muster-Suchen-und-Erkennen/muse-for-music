"""Module containing API Endpoints for data Resources."""

from flask_restx import fields, Resource  # noqa

from .. import api  # noqa

from . import people  # noqa
from . import opus  # noqa
from . import part  # noqa
from . import subpart  # noqa

from . import history  # noqa
