from flask import url_for, request
from flask_restplus import Resource, fields, abort, marshal
from flask_jwt_extended import jwt_required, fresh_jwt_required, get_jwt_identity, get_jwt_claims

from . import user_api as api
from .import auth_logger, has_roles
from .. import jwt, db

from ..models.users import User, UserRole, RoleEnum

from .authentication import user_auth_model

ns = api.namespace('manage', description='User Management Resources:')


password_reset_model = api.model('PasswordReset', {
    'password': fields.String(required=True, example='admin')
})

user_role = api.model('UserRoleModel', {
    'role': fields.String(attribute="role.name", enum=[en.name for en in RoleEnum]),
})

user_model = api.model('UserModel', {
    'username': fields.String(required=True),
    'roles': fields.Nested(user_role, as_list=True),
})

@ns.route('/users/')
class UsersResource(Resource):

    @ns.marshal_list_with(user_model)
    @jwt_required
    @has_roles(roles=[RoleEnum.admin])
    def get(self):
        users = User.query.all()
        return users

    @ns.doc(model=user_model)
    @ns.expect(user_auth_model)
    @fresh_jwt_required
    @has_roles(roles=[RoleEnum.admin])
    def post(self):
        user = User(api.payload.get('username', None), api.payload.get('password', None))
        db.session.add(user)
        db.session.commit()
        return marshal(user, user_model)



@ns.route('/users/<string:username>/')
class UserResource(Resource):

    @ns.marshal_with(user_model)
    @jwt_required
    @has_roles(roles=[RoleEnum.admin])
    def get(self, username: str):
        user = User.get_user_by_name(username)
        if user is None:
            abort()
        return user

    @ns.expect(password_reset_model)
    @fresh_jwt_required
    @has_roles(roles=[RoleEnum.admin])
    def post(self, username: str):
        if username == get_jwt_identity():
            abort(400, 'Admins cant reset their own password.')
        user = User.get_user_by_name(username)
        if user is None:
            abort()
        password = api.payload.get('password', None);
        if password is None:
            abort(400, 'Password must not be empty!')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()


    @fresh_jwt_required
    @has_roles(roles=[RoleEnum.admin])
    def delete(self, username: str):
        if username == get_jwt_identity():
            abort(400, 'User can NOT delete itself!')
        user = User.get_user_by_name(username)
        if user is None:
            abort()
        db.session.delete(user)
        db.session.commit()


@ns.route('/users/<string:username>/roles')
class UserRoleResource(Resource):

    @ns.marshal_list_with(user_role)
    @jwt_required
    @has_roles(roles=[RoleEnum.admin])
    def get(self, username: str):
        user = User.get_user_by_name(username)
        if user is None:
            abort()
        return user.roles

    @ns.marshal_list_with(user_role)
    @ns.expect(user_role)
    @fresh_jwt_required
    @has_roles(roles=[RoleEnum.admin])
    def post(self, username: str):
        user = User.get_user_by_name(username)
        if user is None:
            abort()
        new_role = RoleEnum[api.payload.get('role', 'user')]
        if new_role not in {role.role for role in user.roles}:
            role = UserRole(user, new_role)
            db.session.add(role)
            db.session.commit()
        return user.roles

    @ns.marshal_list_with(user_role)
    @ns.expect(user_role)
    @fresh_jwt_required
    @has_roles(roles=[RoleEnum.admin])
    def delete(self, username: str):
        if username == get_jwt_identity():
            if api.payload.get('role', None) == RoleEnum.admin.name:
                abort(400, 'Admin user can NOT remove admin role on itself!')
        user = User.get_user_by_name(username)
        if user is None:
            abort()
        for role in user.roles:
            if role.role.name == api.payload.get('role', None):
                db.session.delete(role)
        db.session.commit()
        return user.roles
