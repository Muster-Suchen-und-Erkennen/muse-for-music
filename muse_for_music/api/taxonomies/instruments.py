from flask import jsonify, url_for
from flask_restplus import Resource, marshal

from . import ns

from .models import tree_model, tree_model_json


@ns.route('/instruments')
class TestItems(Resource):

    @ns.response(200, 'Success', tree_model_json)
    def get(self):
        test = {
            'name': 'root',
            'children': [
                {
                    'name': 'child1',
                    'children': [
                        {
                            'name': 'leaf1'
                        }
                    ]
                },
                {
                    'name': 'child2'
                }
            ]
        }
        return marshal(test, tree_model), 200

