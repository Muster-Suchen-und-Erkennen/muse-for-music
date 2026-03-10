from typing import List

from flask import jsonify, request, url_for
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_restx import Resource, abort, marshal
from sqlalchemy.sql import select

from ... import db
from ...models.data.history import History, MethodEnum
from ...models.data.opus import Opus
from ...models.data.part import Part
from ...models.data.people import Person
from ...models.data.subpart import SubPart
from ...models.data.voice import Voice
from ...models.users import User
from ...user_api import RoleEnum, has_roles
from . import api
from .models import history_get

ns = api.namespace("history", description="Resource for history.", path="/history")


@ns.route("/")
class HistoryResource(Resource):

    @ns.marshal_with(history_get)
    @jwt_required()
    @has_roles([RoleEnum.admin])
    def get(self):
        q = select(History).order_by(History.time.desc())
        hist = db.session.execute(q).scalars().all()
        return [h for h in hist if h.full_resource or h.method == MethodEnum.delete]


@ns.route("/<string:username>/")
class UserHistoryResource(Resource):

    @ns.marshal_with(history_get)
    @jwt_required()
    def get(self, username):
        if username != get_jwt_identity():
            claims = get_jwt().get("user_claims", [])  # FIXME claim
            if RoleEnum.admin.name not in claims:
                abort(403, "Only admin users can access history of other users.")
        user = User.get_user_by_name(username)
        q = (
            select(History)
            .where(History.user_id == user.id)
            .order_by(History.time.desc())
        )
        hist = db.session.execute(q).scalars().all()
        return [h for h in hist if h.full_resource or h.method == MethodEnum.delete]
