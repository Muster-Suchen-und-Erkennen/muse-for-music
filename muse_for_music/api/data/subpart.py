"""Module for the subparts resource."""

from flask import jsonify, url_for, request
from flask_restplus import Resource, marshal, abort
from sqlalchemy.exc import IntegrityError


from . import api

from .models import subpart_get, subpart_put, voice_get, voice_post, voice_put

from ... import db
from ...models.data.subpart import SubPart
from ...models.data.voice import Voice
from ...models.taxonomies import Anteil, InstrumentierungEinbettungQualitaet, \
                                 InstrumentierungEinbettungQuantitaet


ns = api.namespace('subpart', description='Resource for Subparts.', path='/subparts')


@ns.route('/')
class SubPartListResource(Resource):

    @ns.marshal_list_with(subpart_get)
    def get(self):
        return SubPart.query.all()


@ns.route('/<int:subpart_id>/')
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


@ns.route('/<int:subpart_id>/voices/')
class SubPartVoiceListResource(Resource):

    @ns.marshal_list_with(voice_get)
    @ns.response(404, 'Subpart not found.')
    def get(self, subpart_id):
        subpart = SubPart.get_by_id(subpart_id)  # type: SubPart
        if subpart is None:
            abort(404, 'Requested subpart not found!')
        return subpart.voices

    @ns.doc(model=voice_get, body=voice_post)
    @ns.response(404, 'Subpart not found.')
    def post(self, subpart_id):
        subpart = SubPart.get_by_id(subpart_id)  # type: SubPart
        if subpart is None:
            abort(404, 'Requested subpart not found!')

        new_values = request.get_json()

        new_voice = Voice(subpart, **new_values)
        db.session.add(new_voice)
        db.session.commit()
        return marshal(new_voice, voice_get)


@ns.route('/<int:subpart_id>/voices/<int:voice_id>/')
class SubPartVoiceResource(Resource):

    @ns.marshal_with(voice_get)
    @ns.response(404, 'voice not found.')
    def get(self, subpart_id, voice_id):
        voice = Voice.get_by_id(voice_id)  # type: Voice
        if voice is None:
            abort(404, 'Requested voice not found!')
        return voice

    @ns.doc(model=voice_get, body=voice_put)
    @ns.response(404, 'voice not found.')
    def put(self, subpart_id, voice_id):
        voice = Voice.get_by_id(voice_id)  # type: Voice
        if voice is None:
            abort(404, 'Requested voice not found!')

        new_values = request.get_json()

        voice.update(new_values)
        return marshal(voice, voice_get)

    @ns.response(404, 'voice not found.')
    def delete(self, subpart_id, voice_id):
        voice = Voice.get_by_id(voice_id)  # type: Voice
        if voice is None:
            abort(404, 'Requested voice not found!')
        db.session.delete(voice)
        db.session.commit()
