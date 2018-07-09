import enum
from typing import Union, Sequence
from json import dumps
from sqlalchemy.sql import func
from flask_jwt_extended import get_jwt_identity

from ... import db
from ..users import User
from .people import Person
from .opus import Opus
from .part import Part
from .subpart import SubPart
from .voice import Voice


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
    resource = db.Column(db.String(191))

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
            self.resource = dumps({'id': resource.id}, sort_keys=True)
        if isinstance(resource, Opus):
            self.type = TypeEnum.opus
            self.resource = dumps({'id': resource.id}, sort_keys=True)
        if isinstance(resource, Part):
            self.type = TypeEnum.part
            self.resource = dumps({'id': resource.id, 'opus_id': resource.opus_id}, sort_keys=True)
        if isinstance(resource, SubPart):
            self.type = TypeEnum.subpart
            self.resource = dumps({'id': resource.id, 'part_id': resource.part_id}, sort_keys=True)
        if isinstance(resource, Voice):
            self.type = TypeEnum.voice
            self.resource = dumps({'id': resource.id, 'subpart_id': resource.subpart_id}, sort_keys=True)

    @classmethod
    def isOwner(cls, resource, user: [str, User]=None):
        if user is None:
            user = get_jwt_identity()
        if isinstance(user, str):
            user = User.get_user_by_name(user)
        if user is None:
            return False
        type = None
        resource_id = None
        if isinstance(resource, Person):
            type = TypeEnum.person
            resource_id = dumps({'id': resource.id}, sort_keys=True)
        if isinstance(resource, Opus):
            type = TypeEnum.opus
            resource_id = dumps({'id': resource.id}, sort_keys=True)
        if isinstance(resource, Part):
            type = TypeEnum.part
            resource_id = dumps({'id': resource.id, 'opus_id': resource.opus_id}, sort_keys=True)
        if isinstance(resource, SubPart):
            type = TypeEnum.subpart
            resource_id = dumps({'id': resource.id, 'part_id': resource.part_id}, sort_keys=True)
        if isinstance(resource, Voice):
            type = TypeEnum.voice
            resource_id = dumps({'id': resource.id, 'subpart_id': resource.subpart_id}, sort_keys=True)
        result = cls.query.filter(cls.user == user, cls.method == MethodEnum.create, cls.type == type, cls.resource == resource_id).first()
        return result is not None


class Backup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, server_default=func.now())
    type = db.Column(db.Enum(TypeEnum))
    resource = db.Column(db.Text())

    def __init__(self, resource_type: TypeEnum, resource: str):
        self.type = resource_type
        self.resource = resource
