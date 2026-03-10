"""Module for part resource"""

from flask import jsonify, url_for, request
from flask_restx import Resource, marshal, abort
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import select, delete

from json import dumps

from . import api

from .models import part_get, part_small, part_post, part_put, subpart_get, subpart_post

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

    @ns.marshal_list_with(part_small)
    @jwt_required()
    def get(self):
        q = select(Part)
        return db.session.execute(q).scalars().all()


@ns.route('/<int:id>/')
class PartResource(Resource):

    @ns.marshal_with(part_get)
    @ns.response(404, 'Part not found.')
    @jwt_required()
    def get(self, id):
        part = Part.get_by_id(id)
        if part is None:
            abort(404, 'Requested part not found!')
        return part

    @ns.doc(model=part_get, expect=[part_put], validate=True)
    @ns.response(404, 'Part not found.')
    @jwt_required()
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def put(self, id):
        part = Part.get_by_id(id)
        if part is None:
            abort(404, 'Requested part not found!')
        new_values = request.get_json()

        part.update(new_values)

        username = get_jwt_identity()
        user = User.get_user_by_name(username)
        del_q = delete(History).where(History.user_id == user.id,
                             History.method == MethodEnum.update,
                             History.resource == History.fingerprint(part))
        db.session.execute(del_q)
        hist = History(MethodEnum.update, part, user)
        db.session.add(hist)

        db.session.commit()
        return marshal(part, part_get)

    @ns.response(404, 'Part not found.')
    @jwt_required()
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def delete(self, id):
        part = Part.get_by_id(id)
        if part is None:
            abort(404, 'Requested part not found!')
        if RoleEnum.admin.name not in get_jwt().get("user_claims", []) and not History.isOwner(part):  # FIXME claim
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
    @jwt_required()
    def get(self, id):
        q = select(SubPart).where(SubPart.part_id==id)
        return db.session.execute(q).scalars().all()

    @ns.doc(model=subpart_get, expect=[subpart_post], validate=True)
    @jwt_required()
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


