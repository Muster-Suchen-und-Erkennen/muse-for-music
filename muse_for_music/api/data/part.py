"""Module for part resource"""

from flask import jsonify, url_for, request
from flask_restplus import Resource, marshal, abort
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from json import dumps

from . import api

from .models import part_get, part_post, part_put, subpart_get, subpart_post

from ... import db
from ...user_api import has_roles, RoleEnum
from ...models.users import User
from ...models.data.part import Part
from ...models.data.subpart import SubPart
from ...models.data.measure import Measure
from ...models.taxonomies import InstrumentierungEinbettungQuantitaet, \
                                 InstrumentierungEinbettungQualitaet, \
                                 Lautstaerke, LautstaerkeEinbettung, \
                                 TempoEinbettung, TempoEntwicklung
from ...models.data.history import History, MethodEnum, TypeEnum, Backup

from .backup import to_backup_json


ns = api.namespace('part', description='Resource for Parts.', path='/parts')


@ns.route('/')
class PartsListResource(Resource):

    @ns.marshal_list_with(part_get)
    @jwt_required
    def get(self):
        return Part.query.all()


@ns.route('/<int:id>/')
class PartResource(Resource):

    @ns.marshal_with(part_get)
    @ns.response(404, 'Part not found.')
    @jwt_required
    def get(self, id):
        part = Part.get_by_id(id)  # type: Part
        if part is None:
            abort(404, 'Requested part not found!')
        return part

    @ns.doc(model=part_get, body=part_put)
    @ns.response(404, 'Part not found.')
    @jwt_required
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def put(self, id):
        part = Part.get_by_id(id)  # type: Part
        if part is None:
            abort(404, 'Requested part not found!')
        new_values = request.get_json()

        part.update(new_values)

        username = get_jwt_identity()
        user = User.get_user_by_name(username)
        History.query.filter(History.user_id == user.id,
                             History.method == MethodEnum.update,
                             History.resource == History.fingerprint(part)).delete()
        hist = History(MethodEnum.update, part, user)
        db.session.add(hist)

        db.session.commit()
        return marshal(part, part_get)

    @ns.response(404, 'Part not found.')
    @jwt_required
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def delete(self, id):
        part = Part.get_by_id(id)  # type: Part
        if part is None:
            abort(404, 'Requested part not found!')
        if RoleEnum.admin.name not in get_jwt_claims() and not History.isOwner(part):
            abort(403, 'Only the owner of a resource and Administrators can delete a resource!')
        hist = History(MethodEnum.delete, part)
        db.session.add(hist)
        backup = Backup(TypeEnum.part, dumps(to_backup_json(part)))
        db.session.add(backup)
        db.session.delete(part)
        db.session.commit()


@ns.route('/<int:id>/subparts/')
class PartSubpartsResource(Resource):

    @ns.marshal_list_with(subpart_get)
    @jwt_required
    def get(self, id):
        subparts = SubPart.query.filter_by(part_id=id).all()
        return subparts

    @ns.doc(model=subpart_get, body=subpart_post)
    @jwt_required
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def post(self, id):
        new_values = request.get_json()
        new_values['part_id'] = id
        new_subpart = SubPart(**new_values)
        db.session.add(new_subpart)
        hist = History(MethodEnum.create, new_subpart)
        db.session.add(hist)
        db.session.commit()
        return marshal(new_subpart, subpart_get)


