from flask import jsonify, url_for, request
from flask_restplus import Resource, marshal, abort
from sqlalchemy.exc import IntegrityError


from . import api

from .models import part_get, part_post, part_put

from ... import db
from ...models.data.part import Part
from ...models.data.measure import Measure
from ...models.taxonomies import InstrumentierungEinbettungQuantitaet, \
                                 InstrumentierungEinbettungQualitaet, \
                                 Lautstaerke, LautstaerkeEinbettung, \
                                 TempoEinbettung, TempoEntwicklung


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

        if 'instrumentation_context' in new_values:
            context = part.instrumentation_context
            # quantity
            id_before = new_values['instrumentation_quantity_before']['id']
            id_after = new_values['instrumentation_quantity_after']['id']
            context.instr_quantity_before = InstrumentierungEinbettungQuantitaet.get_by_id(id_before)
            context.instr_quantity_after = InstrumentierungEinbettungQuantitaet.get_by_id(id_after)
            # quality
            id_before = new_values['instrumentation_quantity_before']['id']
            id_after = new_values['instrumentation_quantity_after']['id']
            context.instr_quality_before = InstrumentierungEinbettungQualitaet.get_by_id(id_before)
            context.instr_quality_after = InstrumentierungEinbettungQualitaet.get_by_id(id_after)

        if 'dynamic_context' in new_values:
            context = part.dynamic_context
            # loudness
            id_before = new_values['loudness_before']['id']
            id_after = new_values['loudness_after']['id']
            context.loudness_before = Lautstaerke.get_by_id(id_before)
            context.loudness_after = Lautstaerke.get_by_id(id_after)
            # dynamic trend
            id_before = new_values['dynamic_trend_before']['id']
            id_after = new_values['dynamic_trend_after']['id']
            context.dynamic_trend_before = LautstaerkeEinbettung.get_by_id(id_before)
            context.dynamic_trend_after = LautstaerkeEinbettung.get_by_id(id_after)

        if 'tempo_context' in new_values:
            context = part.tempo_context
            # context
            id_before = new_values['tempo_context_before']['id']
            id_after = new_values['tempo_context_after']['id']
            context.tempo_context_before = TempoEinbettung.get_by_id(id_before)
            context.tempo_context_after = TempoEinbettung.get_by_id(id_after)
            # trend
            id_before = new_values['tempo_trend_before']['id']
            id_after = new_values['tempo_trend_after']['id']
            context.tempo_trend_before = TempoEntwicklung.get_by_id(id_before)
            context.tempo_trend_after = TempoEntwicklung.get_by_id(id_after)

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


