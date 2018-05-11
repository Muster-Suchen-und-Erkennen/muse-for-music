from flask import url_for, request
from flask_restplus import Resource, fields, abort
from flask_jwt_extended import jwt_required, create_access_token, \
                               get_jwt_identity, create_refresh_token, \
                               get_jwt_claims, jwt_refresh_token_required, \
                               fresh_jwt_required

from . import user_api as api
from .import auth_logger
from .. import jwt, db

from ..models.users import User, UserRole, RoleEnum


ns = api.namespace('auth', description='Authentication Resources:')


user_auth_model = api.model('UserAuth', {
    'username': fields.String(required=True, example='admin'),
    'password': fields.String(required=True, example='admin')
})

password_change_model = api.model('PasswordChange', {
    'password': fields.String(required=True, example='admin'),
    'password_repeat': fields.String(required=False, example='admin')
})

jwt_response = api.model('JWT', {
    'access_token': fields.String(required=True)
})

jwt_response_full = api.inherit('JWT_FULL', jwt_response, {
    'refresh_token': fields.String(reqired=True)
})

user_model = api.model('UserModel', {
    'username': fields.String(required=True),
    'roles': fields.List(fields.String())
})


def login_user():
    """Login a user."""
    username = api.payload.get('username', None)
    password = api.payload.get('password', None)
    user = User.get_user_by_name(username)
    if not user:
        auth_logger.debug('Attempted login with unknown username "%s".', username)
        abort(401, 'Wrong username or pasword.')
    if not user.check_password(password):
        auth_logger.error('Attempted login with invalid password for user "%s"', username)
        abort(401, 'Wrong username or pasword.')

    auth_logger.info('New login from user "%s"', username)
    return user


@ns.route('/login/')
class Login(Resource):
    """Login resource."""

    @api.doc(security=None)
    @api.marshal_with(jwt_response_full)
    @api.response(401, 'Wrong username or pasword.')
    @api.expect(user_auth_model)
    def post(self):
        """Login with username and password to get a new token and refresh token."""
        user = login_user()

        ret = {
            'access_token': create_access_token(identity=user, fresh=True),
            'refresh_token': create_refresh_token(identity=user)
        }
        return ret


@ns.route('/fresh-login/')
class FreshLogin(Resource):
    """Resource for a fresh login token without refresh token."""

    @api.doc(security=None)
    @api.marshal_with(jwt_response)
    @api.response(401, 'Wrong username or pasword.')
    @api.expect(user_auth_model)
    def post(self):
        """Login with username and password to get a fresh token."""
        user = login_user()

        ret = {
            'access_token': create_access_token(identity=user, fresh=True),
            'refresh_token': create_refresh_token(identity=user)
        }
        return ret


@ns.route('/change-password/')
class ChangePassword(Resource):
    """Resource to change user passsword."""

    @api.expect(password_change_model)
    @api.response(401, 'Not Authenticated')
    @fresh_jwt_required
    def post(self):
        """Change user password."""
        user = User.get_user_by_name(get_jwt_identity())
        password = api.payload.get('password', None)
        if password is None:
            abort(400, 'Incorrect password or password_repeat.')
        if password != api.payload.get('password_repeat', None):
            abort(400, 'Incorrect password or password_repeat.')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()


@ns.route('/check/')
class Check(Resource):
    """Resource to check access tokens."""

    @api.marshal_with(user_model)
    @api.response(401, 'Not Authenticated')
    @jwt_required
    def get(self):
        """Check your current access token."""
        ret = {
            'username': get_jwt_identity(),
            'roles': get_jwt_claims()
        }
        return ret


@ns.route('/refresh/')
class Refresh(Resource):
    """Resource to refresh access tokens."""

    @api.doc(security=['jwt-refresh'])
    @api.marshal_with(jwt_response)
    @api.response(401, 'Wrong username or pasword.')
    @jwt_refresh_token_required
    def post(self):
        """Create a new access token with a refresh token."""
        username = get_jwt_identity()
        user = User.get_user_by_name(username)
        if not user:
            abort(401, "User doesn't exist.")
        auth_logger.debug('User "%s" asked for a new access token.', username)
        new_token = create_access_token(identity=user, fresh=False)
        ret = {'access_token': new_token}
        return ret, 200
