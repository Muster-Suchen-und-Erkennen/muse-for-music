"""Module for the opus resource."""


from flask import jsonify, url_for, request
from flask_restplus import Resource, marshal, abort
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from json import dumps

from . import api

from .models import opus_post, opus_put, opus_get, parse_date, opus_get, opus_post, \
                    part_get, part_post

from ... import db
from ...user_api import has_roles, RoleEnum
from ...models.users import User
from ...models.data.opus import Opus
from ...models.data.part import Part
from ...models.data.history import History, MethodEnum, TypeEnum, Backup

from .backup import to_backup_json

ns = api.namespace('opus', description='Resource for opuses.', path='/opuses')


@ns.route('/')
class OpusListResource(Resource):

    @ns.marshal_list_with(opus_get)
    @jwt_required
    def get(self):
        return Opus.query.all()

    @ns.doc(model=opus_get, body=opus_post)
    @ns.response(409, 'Name is not unique.')
    @jwt_required
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def post(self):
        new_opus = Opus(**request.get_json())
        try:
            db.session.add(new_opus)
            hist = History(MethodEnum.create, new_opus)
            db.session.add(hist)
            db.session.commit()
            return marshal(new_opus, opus_get)
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500, str(err))


@ns.route('/<int:id>/')
class OpusResource(Resource):

    @ns.marshal_with(opus_get)
    @ns.response(404, 'Opus not found.')
    @jwt_required
    def get(self, id):
        opus = Opus.get_by_id(id)  # type: Opus
        if opus is None:
            abort(404, 'Requested opus not found!')
        return opus

    @ns.doc(model=opus_get, body=opus_put)
    @ns.response(404, 'Opus not found.')
    @jwt_required
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def put(self, id):
        opus = Opus.get_by_id(id)  # type: Opus
        if opus is None:
            abort(404, 'Requested opus not found!')
        new_values = request.get_json()

        opus.update(new_values)
        username = get_jwt_identity()
        user = User.get_user_by_name(username)
        History.query.filter(History.user_id == user.id,
                             History.method == MethodEnum.update,
                             History.resource == History.fingerprint(opus)).delete()
        hist = History(MethodEnum.update, opus, user)
        db.session.add(hist)
        db.session.commit()
        return marshal(opus, opus_get)

    @ns.response(404, 'Opus not found.')
    @jwt_required
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def delete(self, id):
        opus = Opus.get_by_id(id)  # type: Opus
        if opus is None:
            abort(404, 'Requested opus not found!')
        if RoleEnum.admin.name not in get_jwt_claims() and not History.isOwner(opus):
            abort(403, 'Only the owner of a resource and Administrators can delete a resource!')
        hist = History(MethodEnum.delete, opus)
        db.session.add(hist)
        backup = Backup(TypeEnum.opus, dumps(to_backup_json(opus)))
        db.session.add(backup)
        db.session.delete(opus)
        db.session.commit()




@ns.route('/<int:id>/parts/')
class OpusPartsResource(Resource):

    @ns.marshal_list_with(part_get)
    @jwt_required
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def get(self, id):
        parts = Part.query.filter_by(opus_id=id).all()
        return parts

    @ns.doc(model=part_get, body=part_post)
    @jwt_required
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def post(self, id):
        new_values = request.get_json()
        new_values['opus_id'] = id
        new_part = Part(**new_values)
        db.session.add(new_part)
        hist = History(MethodEnum.create, new_part)
        db.session.add(hist)
        db.session.commit()
        return marshal(new_part, part_get)
