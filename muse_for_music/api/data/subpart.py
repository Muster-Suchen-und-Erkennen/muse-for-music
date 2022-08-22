"""Module for the subparts resource."""

from flask import jsonify, url_for, request
from flask_restx import Resource, marshal, abort
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from json import dumps

from . import api

from .models import subpart_get, subpart_put, voice_get, voice_post, voice_put

from ... import db
from ...user_api import has_roles, RoleEnum
from ...models.users import User
from ...models.data.subpart import SubPart
from ...models.data.voice import Voice
from ...models.taxonomies import Anteil, InstrumentierungEinbettungQualitaet, \
                                 InstrumentierungEinbettungQuantitaet
from ...models.data.history import History, MethodEnum, TypeEnum, Backup

from .backup import to_backup_json


ns = api.namespace('subpart', description='Resource for Subparts.', path='/subparts')


@ns.route('/')
class SubPartListResource(Resource):

    @ns.marshal_list_with(subpart_get)
    @jwt_required
    def get(self):
        return SubPart.query.all()


@ns.route('/<int:subpart_id>/')
class SubPartResource(Resource):

    @ns.marshal_with(subpart_get)
    @ns.response(404, 'Subpart not found.')
    @jwt_required
    def get(self, subpart_id):
        subpart = SubPart.get_by_id(subpart_id)  # type: SubPart
        if subpart is None:
            abort(404, 'Requested subpart not found!')
        return subpart

    @ns.doc(model=subpart_get, body=subpart_put)
    @ns.response(404, 'Subpart not found.')
    @jwt_required
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def put(self, subpart_id):
        subpart = SubPart.get_by_id(subpart_id)  # type: SubPart
        if subpart is None:
            abort(404, 'Requested subpart not found!')

        new_values = request.get_json()

        subpart.update(new_values)

        username = get_jwt_identity()
        user = User.get_user_by_name(username)
        History.query.filter(History.user_id == user.id,
                             History.method == MethodEnum.update,
                             History.resource == History.fingerprint(subpart)).delete()
        hist = History(MethodEnum.update, subpart, user)
        db.session.add(hist)

        db.session.commit()
        return marshal(subpart, subpart_get)

    @ns.response(404, 'Subpart not found.')
    @jwt_required
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def delete(self, subpart_id):
        subpart = SubPart.get_by_id(subpart_id)  # type: SubPart
        if subpart is None:
            abort(404, 'Requested subpart not found!')
        if RoleEnum.admin.name not in get_jwt_claims() and not History.isOwner(subpart):
            abort(403, 'Only the owner of a resource and Administrators can delete a resource!')
        hist = History(MethodEnum.delete, subpart)
        db.session.add(hist)
        backup = Backup(TypeEnum.subpart, dumps(to_backup_json(subpart)))
        db.session.add(backup)
        db.session.delete(subpart)
        db.session.commit()


@ns.route('/<int:subpart_id>/voices/')
class SubPartVoiceListResource(Resource):

    @ns.marshal_list_with(voice_get)
    @ns.response(404, 'Subpart not found.')
    @jwt_required
    def get(self, subpart_id):
        subpart = SubPart.get_by_id(subpart_id)  # type: SubPart
        if subpart is None:
            abort(404, 'Requested subpart not found!')
        return subpart.voices

    @ns.doc(model=voice_get, body=voice_post)
    @ns.response(404, 'Subpart not found.')
    @jwt_required
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def post(self, subpart_id):
        subpart = SubPart.get_by_id(subpart_id)  # type: SubPart
        if subpart is None:
            abort(404, 'Requested subpart not found!')

        new_values = request.get_json()

        new_voice = Voice(subpart, **new_values)
        db.session.add(new_voice)
        hist = History(MethodEnum.create, new_voice)
        db.session.add(hist)
        db.session.commit()
        return marshal(new_voice, voice_get)


@ns.route('/<int:subpart_id>/voices/<int:voice_id>/')
class SubPartVoiceResource(Resource):

    @ns.marshal_with(voice_get)
    @ns.response(404, 'voice not found.')
    @jwt_required
    def get(self, subpart_id, voice_id):
        voice = Voice.get_by_id(voice_id)  # type: Voice
        if voice is None:
            abort(404, 'Requested voice not found!')
        return voice

    @ns.doc(model=voice_get, body=voice_put)
    @ns.response(404, 'voice not found.')
    @jwt_required
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def put(self, subpart_id, voice_id):
        voice = Voice.get_by_id(voice_id)  # type: Voice
        if voice is None:
            abort(404, 'Requested voice not found!')

        new_values = request.get_json()

        voice.update(new_values)
        username = get_jwt_identity()
        user = User.get_user_by_name(username)
        History.query.filter(History.user_id == user.id,
                             History.method == MethodEnum.update,
                             History.resource == History.fingerprint(voice)).delete()
        hist = History(MethodEnum.update, voice, user)
        db.session.add(hist)
        db.session.commit()
        return marshal(voice, voice_get)

    @ns.response(404, 'voice not found.')
    @jwt_required
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def delete(self, subpart_id, voice_id):
        voice = Voice.get_by_id(voice_id)  # type: Voice
        if voice is None:
            abort(404, 'Requested voice not found!')
        if RoleEnum.admin.name not in get_jwt_claims() and not History.isOwner(voice):
            abort(403, 'Only the owner of a resource and Administrators can delete a resource!')
        hist = History(MethodEnum.delete, voice)
        db.session.add(hist)
        backup = Backup(TypeEnum.voice, dumps(to_backup_json(voice)))
        db.session.add(backup)
        db.session.delete(voice)
        db.session.commit()
