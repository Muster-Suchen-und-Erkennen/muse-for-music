from flask_restplus import fields, Resource

from .. import api

ns = api.namespace('data', description='All data objects.')

from . import people
from . import opus
from . import instrumentation


@ns.route('/')
class DataResources(Resource):

    #@ns.marshal_list_with(api_resource)
    def get(self):
        data_endpoints = [
            {
                'name': 'people',
                'description': 'test'
            },
            {
                'name': 'opus',
                'description': 'test'
            }
        ]
        return data_endpoints

