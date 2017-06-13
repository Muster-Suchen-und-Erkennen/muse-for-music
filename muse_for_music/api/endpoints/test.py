from flask import jsonify, url_for
from flask_restplus import Resource

from .. import api

ns = api.namespace('test', description='A simple Test Namespace.')


@ns.route('/')
class TestItems(Resource):

    def get(self):
        return {
            'children': [
                {
                    'name': 'items',
                    'ref': url_for('api.test_test_items') + 'items'
                }
            ]
        }

