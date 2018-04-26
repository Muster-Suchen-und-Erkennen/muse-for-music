import enum
from typing import Union, Sequence
from json import dumps
from sqlalchemy.sql import func
from flask_jwt_extended import get_jwt_identity

from ... import db
from ..users import User
from .people import Person


class MethodEnum(enum.Enum):
    create = 1
    update = 2
    delete = 3


class TypeEnum(enum.Enum):
    person = 1
    opus = 2
    part = 3
    subpart = 4
    voice = 5


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, server_default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    method = db.Column(db.Enum(MethodEnum))
    type = db.Column(db.Enum(TypeEnum))
    resource = db.Column(db.String())

    user = db.relationship(User)

    def __init__(self, method: MethodEnum, resource, user: Union[str, User]=None):
        if user is None:
            user = get_jwt_identity()
        if isinstance(user, str):
            user = User.get_user_by_name(user)
        self.user = user
        self.method = method
        if method == MethodEnum.create:
            db.session.flush((resource,))
        if isinstance(resource, Person):
            self.type = TypeEnum.person
            self.resource = dumps({'id': resource.id})
