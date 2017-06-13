from flask import url_for, request
from flask_restplus import Resource, fields, abort
from flask_jwt_extended import jwt_required, fresh_jwt_required, get_jwt_identity, get_jwt_claims

from . import user_api as api
from .import auth_logger, has_roles
from .. import jwt

from ..models.users import User, UserRole, RoleEnum


ns = api.namespace('manage', description='User Management Resources:')


@ns.route('/user')
class Users(Resource):

    @jwt_required
    @has_roles(roles=[RoleEnum.admin])
    def get(self):
        return []
