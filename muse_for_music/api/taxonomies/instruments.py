from flask import jsonify, url_for
from flask_restplus import Resource, marshal

from . import ns

from .models import tree_model, tree_model_json

from ...models.taxonomies.instruments import Instrument


@ns.route('/instruments')
class TestItems(Resource):

    @ns.response(200, 'Success', tree_model_json)
    def get(self):
        return marshal(Instrument.get_root(), tree_model), 200

