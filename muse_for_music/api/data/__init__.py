from flask_restplus import fields, Resource

from .. import api
from ..models import api_resource

ns = api.namespace('data', description='All data objects.')

from . import people


@ns.route('/')
class DataResources(Resource):

    @ns.marshal_list_with(api_resource)
    def get(self):
        data_endpoints = [
            {
                'name': 'chords',
                'description': 'test'
            },
            {
                'name': 'instruments',
                'description': 'test'
            }
        ]
        return data_endpoints

