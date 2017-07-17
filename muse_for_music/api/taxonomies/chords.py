from flask import jsonify, url_for
from flask_restplus import Resource, marshal

from . import ns

from .models import tree_model, tree_model_json

from ...models.taxonomies.chords import Akkord


@ns.route('/chords')
class ChordsResource(Resource):

    @ns.response(200, 'Success', tree_model_json)
    def get(self):
        return marshal(Akkord.get_root(), tree_model), 200

