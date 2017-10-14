from flask import jsonify, url_for, request
from flask_restplus import Resource, marshal, abort
from sqlalchemy.exc import IntegrityError


from . import api

from .models import subpart_get, subpart_post

from ... import db
from ...models.data.subpart import SubPart
from ...models.taxonomies import Anteil, InstrumentierungEinbettungQualitaet, \
                                 InstrumentierungEinbettungQuantitaet


ns = api.namespace('subpart', description='TODO.')


@ns.route('/<int:subpart_id>')
class SubPartResource(Resource):

    @ns.marshal_with(subpart_get)
    def get(self, subpart_id):
        subpart = SubPart.get_by_id(subpart_id)  # type: SubPart
        if subpart is None:
            abort(404, 'Requested subpart not found!')
        return subpart

    def put(self, subpart_id):
        subpart = SubPart.get_by_id(subpart_id)  # type: SubPart
        if subpart is None:
            abort(404, 'Requested subpart not found!')

        new_values = request.get_json()

        subpart.update(new_values)

        db.session.commit()

    @ns.response(404, 'Subpart not found.')
    def delete(self, subpart_id):
        subpart = SubPart.get_by_id(subpart_id)  # type: SubPart
        if subpart is None:
            abort(404, 'Requested subpart not found!')
        db.session.delete(subpart)
        db.session.commit()

