"""Module for the opus resource."""

from http import HTTPStatus
from json import dumps

from flask import request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_restx import Resource, marshal
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import delete, select

from ... import db
from ...models.data.history import Backup, History, MethodEnum, TypeEnum
from ...models.data.opus import Opus
from ...models.data.part import Part
from ...models.users import User
from ...user_api import RoleEnum, has_roles
from ...util import abort
from . import api
from .backup import to_backup_json
from .models import (
    opus_post,
    opus_put,
    opus_small,
    opus_small_get,
    part_get,
    part_post,
    part_small,
    part_small_get,
)

ns = api.namespace("opus", description="Resource for opuses.", path="/opuses")


@ns.route("/")
class OpusListResource(Resource):

    @ns.marshal_list_with(opus_small)
    @jwt_required()
    def get(self):
        q = select(Opus)
        return db.session.execute(q).scalars().all()

    @ns.doc(model=opus_small_get, expect=[opus_post], validate=True)
    @ns.response(HTTPStatus.CONFLICT, "Name is not unique.")
    @jwt_required()
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def post(self):
        new_opus = Opus(**request.get_json())
        try:
            db.session.add(new_opus)
            hist = History(MethodEnum.create, new_opus)
            db.session.add(hist)
            db.session.commit()
            return marshal(new_opus, opus_small_get)
        except IntegrityError as err:
            db.session.rollback()
            if hasattr(err, "orig"):
                err = err.orig
            message = str(err)
            if "UNIQUE constraint failed" in message:
                abort(HTTPStatus.CONFLICT, "Name is not unique!")
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, str(err))


@ns.route("/<int:id>/")
class OpusResource(Resource):

    @ns.marshal_with(opus_small_get)
    @ns.response(HTTPStatus.NOT_FOUND, "Opus not found.")
    @jwt_required()
    def get(self, id):
        opus = Opus.get_by_id(id)
        if opus is None:
            abort(HTTPStatus.NOT_FOUND, "Requested opus not found!")
        return opus

    @ns.doc(model=opus_small_get, expect=[opus_put], validate=True)
    @ns.response(HTTPStatus.NOT_FOUND, "Opus not found.")
    @jwt_required()
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def put(self, id):
        opus = Opus.get_by_id(id)
        if opus is None:
            abort(HTTPStatus.NOT_FOUND, "Requested opus not found!")
        new_values = request.get_json()

        try:
            opus.update(new_values)
            username = get_jwt_identity()
            user = User.get_user_by_name(username)
            assert user is not None  # JWT setup is broken if this fails
            del_q = delete(History).where(
                History.user_id == user.id,
                History.method == MethodEnum.update,
                History.resource == History.fingerprint(opus),
            )
            db.session.execute(del_q)
            hist = History(MethodEnum.update, opus, user)
            db.session.add(hist)
            db.session.commit()
            return marshal(opus, opus_small_get)
        except IntegrityError as err:
            db.session.rollback()
            if hasattr(err, "orig"):
                err = err.orig
            message = str(err)
            if "UNIQUE constraint failed" in message:
                abort(HTTPStatus.CONFLICT, "Name is not unique!")
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, str(err))

    @ns.response(HTTPStatus.NOT_FOUND, "Opus not found.")
    @jwt_required()
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def delete(self, id):
        opus = Opus.get_by_id(id)
        if opus is None:
            abort(HTTPStatus.NOT_FOUND, "Requested opus not found!")
        if RoleEnum.admin.name not in get_jwt().get(
            "user_claims", []
        ) and not History.isOwner(opus):
            abort(
                HTTPStatus.FORBIDDEN,
                "Only the owner of a resource and Administrators can delete a resource!",
            )
        hist = History(MethodEnum.delete, opus)
        db.session.add(hist)
        backup = Backup(TypeEnum.opus, dumps(to_backup_json(opus)))
        db.session.add(backup)
        db.session.delete(opus)
        db.session.commit()


@ns.route("/<int:id>/parts/")
class OpusPartsResource(Resource):

    @ns.marshal_list_with(part_small)
    @jwt_required()
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def get(self, id):
        q = Part.prepare_query(lazy=True).where(Part.opus_id == id)
        return db.session.execute(q).scalars().all()

    @ns.doc(model=part_small_get, expect=[part_post], validate=True)
    @jwt_required()
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def post(self, id):
        new_values = request.get_json()
        new_values["opus_id"] = id
        new_part = Part(**new_values)
        db.session.add(new_part)
        hist = History(MethodEnum.create, new_part)
        db.session.add(hist)
        db.session.commit()
        return marshal(new_part, part_get)
