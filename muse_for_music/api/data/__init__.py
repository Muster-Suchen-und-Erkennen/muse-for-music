from flask_restplus import fields, Resource

from .. import api

from .models import data_model

ns = api.namespace('data', description='All data objects.')

from . import people
from . import opus
from . import part
from . import subpart


@ns.route('/')
class DataResource(Resource):

    @ns.marshal_list_with(data_model)
    def get(self):
        return {}

