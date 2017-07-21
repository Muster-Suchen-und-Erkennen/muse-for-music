from flask import jsonify, url_for
from flask_restplus import Resource, marshal

from . import ns

from .models import list_item_model

from ...models.taxonomies.misc import Anteil, AuftretenWerkausschnitt, AuftretenSatz


@ns.route('/ratio')
class RatioResource(Resource):

    @ns.marshal_list_with(list_item_model)
    def get(self):
        return Anteil.get_all()


@ns.route('/occurrence-in-part')
class OccurrenceInPartResource(Resource):

    @ns.marshal_list_with(list_item_model)
    def get(self):
        return AuftretenWerkausschnitt.get_all()


@ns.route('/occurrence-in-movement')
class OccurrenceInMovementResource(Resource):

    @ns.marshal_list_with(list_item_model)
    def get(self):
        return AuftretenSatz.get_all()

