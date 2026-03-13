from http import HTTPStatus

from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_restx import Resource
from sqlalchemy.sql import select

from ... import db
from ...models.data.history import History, MethodEnum
from ...models.users import User
from ...user_api import RoleEnum, has_roles
from ...util import abort
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
            claims = get_jwt().get("user_claims", [])
            if RoleEnum.admin.name not in claims:
                abort(
                    HTTPStatus.FORBIDDEN,
                    "Only admin users can access history of other users.",
                )
        user = User.get_user_by_name(username)
        assert user is not None  # JWT setup is broken if this fails
        q = (
            select(History)
            .where(History.user_id == user.id)
            .order_by(History.time.desc())
        )
        hist = db.session.execute(q).scalars().all()
        return [h for h in hist if h.full_resource or h.method == MethodEnum.delete]
