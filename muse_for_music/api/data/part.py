from flask import jsonify, url_for, request
from flask_restplus import Resource, marshal, abort
from sqlalchemy.exc import IntegrityError


from . import api

from .models import part_get, part_post, part_put

from ... import db
from ...models.data.part import Part
from ...models.data.measure import Measure


ns = api.namespace('part', description='TODO.')


@ns.route('/')
class PartsListResource(Resource):

    @ns.marshal_list_with(part_get)
    def get(self):
        return Part.query.all()


@ns.route('/<int:id>')
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

        if 'movement' in new_values:
            part.movement = new_values['movement']

        for attribute in ('measure_start', 'measure_end'):
            if attribute in new_values:
                measure = getattr(part, attribute)  # type: Measure
                new = new_values[attribute]
                measure.from_page = new['from_page']
                measure.measure = new['measure']
                db.session.add(measure)

        if 'occurence_in_movement' in new_values:
            pass

        db.session.add(part)
        db.session.commit()
        return marshal(part, part_get)

    @ns.response(404, 'Part not found.')
    def delete(self, id):
        part = Part.get_by_id(id)  # type: Part
        if part is None:
            abort(404, 'Requested part not found!')
        db.session.delete(part)
        db.session.commit()


