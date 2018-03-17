"""Module for part resource"""

from flask import jsonify, url_for, request
from flask_restplus import Resource, marshal, abort
from sqlalchemy.exc import IntegrityError


from . import api

from .models import part_get, part_post, part_put, subpart_get, subpart_post

from ... import db
from ...models.data.part import Part
from ...models.data.subpart import SubPart
from ...models.data.measure import Measure
from ...models.taxonomies import InstrumentierungEinbettungQuantitaet, \
                                 InstrumentierungEinbettungQualitaet, \
                                 Lautstaerke, LautstaerkeEinbettung, \
                                 TempoEinbettung, TempoEntwicklung


ns = api.namespace('part', description='Resource for Parts.', path='/parts')


@ns.route('/')
class PartsListResource(Resource):

    @ns.marshal_list_with(part_get)
    def get(self):
        return Part.query.all()


@ns.route('/<int:id>/')
class PartResource(Resource):

    @ns.marshal_with(part_get)
    @ns.response(404, 'Part not found.')
    def get(self, id):
        part = Part.get_by_id(id)  # type: Part
        if part is None:
            abort(404, 'Requested part not found!')
        return part

    @ns.doc(model=part_get, body=part_put)
    @ns.response(404, 'Part not found.')
    def put(self, id):
        part = Part.get_by_id(id)  # type: Part
        if part is None:
            abort(404, 'Requested part not found!')
        new_values = request.get_json()

        part.update(new_values)

        db.session.commit()
        return marshal(part, part_get)

    @ns.response(404, 'Part not found.')
    def delete(self, id):
        part = Part.get_by_id(id)  # type: Part
        if part is None:
            abort(404, 'Requested part not found!')
        db.session.delete(part)
        db.session.commit()


@ns.route('/<int:id>/subparts/')
class PartSubpartsResource(Resource):

    @ns.marshal_list_with(subpart_get)
    def get(self, id):
        subparts = SubPart.query.filter_by(part_id=id).all()
        return subparts

    @ns.doc(model=subpart_get, body=subpart_post)
    def post(self, id):
        new_values = request.get_json()
        new_values['part_id'] = id
        new_subpart = SubPart(**new_values)
        db.session.add(new_subpart)
        db.session.commit()
        return marshal(new_subpart, subpart_get)


