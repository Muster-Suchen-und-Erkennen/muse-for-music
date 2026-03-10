"""Module for the subparts resource."""

from json import dumps

from flask import jsonify, request, url_for
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_restx import Resource, abort, marshal
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import delete, select

from ... import db
from ...models.data.history import Backup, History, MethodEnum, TypeEnum
from ...models.data.subpart import SubPart
from ...models.data.voice import Voice
from ...models.taxonomies import (
    Anteil,
    InstrumentierungEinbettungQualitaet,
    InstrumentierungEinbettungQuantitaet,
)
from ...models.users import User
from ...user_api import RoleEnum, has_roles
from . import api
from .backup import to_backup_json
from .models import subpart_get, subpart_put, voice_get, voice_post, voice_put

ns = api.namespace("subpart", description="Resource for Subparts.", path="/subparts")


@ns.route("/")
class SubPartListResource(Resource):

    @ns.marshal_list_with(subpart_get)
    @jwt_required()
    def get(self):
        q = select(SubPart)
        return db.session.execute(q).scalars().all()


@ns.route("/<int:subpart_id>/")
class SubPartResource(Resource):

    @ns.marshal_with(subpart_get)
    @ns.response(404, "Subpart not found.")
    @jwt_required()
    def get(self, subpart_id):
        subpart = SubPart.get_by_id(subpart_id)
        if subpart is None:
            abort(404, "Requested subpart not found!")
        return subpart

    @ns.doc(model=subpart_get, expect=[subpart_put], validate=True)
    @ns.response(404, "Subpart not found.")
    @jwt_required()
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def put(self, subpart_id):
        subpart = SubPart.get_by_id(subpart_id)
        if subpart is None:
            abort(404, "Requested subpart not found!")

        new_values = request.get_json()

        subpart.update(new_values)

        username = get_jwt_identity()
        user = User.get_user_by_name(username)
        del_q = delete(History).where(
            History.user_id == user.id,
            History.method == MethodEnum.update,
            History.resource == History.fingerprint(subpart),
        )
        db.session.execute(del_q)
        hist = History(MethodEnum.update, subpart, user)
        db.session.add(hist)

        db.session.commit()
        return marshal(subpart, subpart_get)

    @ns.response(404, "Subpart not found.")
    @jwt_required()
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def delete(self, subpart_id):
        subpart = SubPart.get_by_id(subpart_id)
        if subpart is None:
            abort(404, "Requested subpart not found!")
        if RoleEnum.admin.name not in get_jwt().get(
            "user_claims", []
        ) and not History.isOwner(
            subpart
        ):  # FIXME claim
            abort(
                403,
                "Only the owner of a resource and Administrators can delete a resource!",
            )
        hist = History(MethodEnum.delete, subpart)
        db.session.add(hist)
        backup = Backup(TypeEnum.subpart, dumps(to_backup_json(subpart)))
        db.session.add(backup)
        db.session.delete(subpart)
        db.session.commit()


@ns.route("/<int:subpart_id>/voices/")
class SubPartVoiceListResource(Resource):

    @ns.marshal_list_with(voice_get)
    @ns.response(404, "Subpart not found.")
    @jwt_required()
    def get(self, subpart_id):
        subpart = SubPart.get_by_id(subpart_id)
        if subpart is None:
            abort(404, "Requested subpart not found!")
        return subpart.voices

    @ns.doc(model=voice_get, expect=[voice_post], validate=True)
    @ns.response(404, "Subpart not found.")
    @jwt_required()
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def post(self, subpart_id):
        subpart = SubPart.get_by_id(subpart_id)
        if subpart is None:
            abort(404, "Requested subpart not found!")

        new_values = request.get_json()

        new_voice = Voice(subpart, **new_values)
        db.session.add(new_voice)
        hist = History(MethodEnum.create, new_voice)
        db.session.add(hist)
        db.session.commit()
        return marshal(new_voice, voice_get)


@ns.route("/<int:subpart_id>/voices/<int:voice_id>/")
class SubPartVoiceResource(Resource):

    @ns.marshal_with(voice_get)
    @ns.response(404, "voice not found.")
    @jwt_required()
    def get(self, subpart_id, voice_id):
        voice = Voice.get_by_id(voice_id)
        if voice is None:
            abort(404, "Requested voice not found!")
        return voice

    @ns.doc(model=voice_get, expect=[voice_put], validate=True)
    @ns.response(404, "voice not found.")
    @jwt_required()
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def put(self, subpart_id, voice_id):
        voice = Voice.get_by_id(voice_id)
        if voice is None:
            abort(404, "Requested voice not found!")

        new_values = request.get_json()

        voice.update(new_values)
        username = get_jwt_identity()
        user = User.get_user_by_name(username)
        del_q = delete(History).where(
            History.user_id == user.id,
            History.method == MethodEnum.update,
            History.resource == History.fingerprint(voice),
        )
        db.session.execute(del_q)
        hist = History(MethodEnum.update, voice, user)
        db.session.add(hist)
        db.session.commit()
        return marshal(voice, voice_get)

    @ns.response(404, "voice not found.")
    @jwt_required()
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def delete(self, subpart_id, voice_id):
        voice = Voice.get_by_id(voice_id)
        if voice is None:
            abort(404, "Requested voice not found!")
        if RoleEnum.admin.name not in get_jwt().get(
            "user_claims", []
        ) and not History.isOwner(
            voice
        ):  # FIXME claim
            abort(
                403,
                "Only the owner of a resource and Administrators can delete a resource!",
            )
        hist = History(MethodEnum.delete, voice)
        db.session.add(hist)
        backup = Backup(TypeEnum.voice, dumps(to_backup_json(voice)))
        db.session.add(backup)
        db.session.delete(voice)
        db.session.commit()
