from flask import jsonify, url_for, request
from flask_restplus import Resource, marshal, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims

from . import api

from .models import history_get

from ... import db
from ...user_api import has_roles, RoleEnum
from ...models.users import User
from ...models.data.history import History
from ...models.data.people import Person
from ...models.data.opus import Opus
from ...models.data.part import Part
from ...models.data.subpart import SubPart
from ...models.data.voice import Voice


ns = api.namespace('history', description='Resource for history.', path='/history')


@ns.route('/')
class HistoryResource(Resource):

    @ns.marshal_with(history_get)
    @jwt_required
    @has_roles([RoleEnum.admin])
    def get(self):
        hist = History.query.order_by(History.time.desc()).all()
        return hist


@ns.route('/<string:username>/')
class UserHistoryResource(Resource):

    @ns.marshal_with(history_get)
    @jwt_required
    def get(self, username):
        if username != get_jwt_identity():
            claims = get_jwt_claims()
            if RoleEnum.admin.name not in claims:
                abort(403, 'Only admin users can access history of other users.')
        user = User.get_user_by_name(username)
        hist = History.query.filter(History.user_id == user.id).order_by(History.time.desc()).all()
        return hist
