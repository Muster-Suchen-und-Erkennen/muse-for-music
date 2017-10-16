from flask import jsonify, url_for, request
from flask_restplus import Resource, marshal, abort
from sqlalchemy.exc import IntegrityError


from . import api

from .models import subpart_get, subpart_put

from ... import db
from ...models.data.subpart import SubPart
from ...models.taxonomies import Anteil, InstrumentierungEinbettungQualitaet, \
                                 InstrumentierungEinbettungQuantitaet


ns = api.namespace('subpart', description='TODO.')


@ns.route('/')
class SubPartListResource(Resource):

    @ns.marshal_list_with(subpart_get)
    def get(self):
        return SubPart.query.all()


@ns.route('/<int:subpart_id>')
class SubPartResource(Resource):

    @ns.marshal_with(subpart_get)
    @ns.response(404, 'Subpart not found.')
    def get(self, subpart_id):
        subpart = SubPart.get_by_id(subpart_id)  # type: SubPart
        if subpart is None:
            abort(404, 'Requested subpart not found!')
        return subpart

    @ns.doc(model=subpart_get, body=subpart_put)
    @ns.response(404, 'Subpart not found.')
    def put(self, subpart_id):
        subpart = SubPart.get_by_id(subpart_id)  # type: SubPart
        if subpart is None:
            abort(404, 'Requested subpart not found!')

        new_values = request.get_json()

        subpart.update(new_values)

        db.session.commit()
        return marshal(subpart, subpart_get)

    @ns.response(404, 'Subpart not found.')
    def delete(self, subpart_id):
        subpart = SubPart.get_by_id(subpart_id)  # type: SubPart
        if subpart is None:
            abort(404, 'Requested subpart not found!')
        db.session.delete(subpart)
        db.session.commit()

