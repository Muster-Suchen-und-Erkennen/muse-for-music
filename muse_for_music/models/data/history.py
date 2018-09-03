import enum
from typing import Union, Sequence
from json import dumps, loads
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

    @staticmethod
    def fromResource(resource: Union[Person, Opus, Part, SubPart, Voice]):
        if isinstance(resource, Person):
            return TypeEnum.person
        elif isinstance(resource, Opus):
            return TypeEnum.opus
        elif isinstance(resource, Part):
            return TypeEnum.part
        elif isinstance(resource, SubPart):
            return TypeEnum.subpart
        elif isinstance(resource, Voice):
            return TypeEnum.voice
        else:
            raise TypeError('Resource has wrong Type ' + str(type(resource)))


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, server_default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    method = db.Column(db.Enum(MethodEnum))
    type = db.Column(db.Enum(TypeEnum))
    resource = db.Column(db.String(191))

    user = db.relationship(User)

    _full_resource = None

    def __init__(self, method: MethodEnum,
                 resource: Union[Person, Opus, Part, SubPart, Voice],
                 user: Union[str, User]=None):
        if user is None:
            user = get_jwt_identity()
        if isinstance(user, str):
            user = User.get_user_by_name(user)
        self.user = user
        self.method = method
        if method == MethodEnum.create:
            db.session.flush((resource,))
        self.type = TypeEnum.fromResource(resource)
        self.resource = History.fingerprint(resource)
        self._full_resource = None

    @staticmethod
    def fingerprint(resource: Union[Person, Opus, Part, SubPart, Voice]):
        if isinstance(resource, Person):
            return dumps({'id': resource.id}, sort_keys=True)
        elif isinstance(resource, Opus):
            return dumps({'id': resource.id}, sort_keys=True)
        elif isinstance(resource, Part):
            return dumps({'id': resource.id, 'opus_id': resource.opus_id}, sort_keys=True)
        elif isinstance(resource, SubPart):
            return dumps({'id': resource.id, 'part_id': resource.part_id}, sort_keys=True)
        elif isinstance(resource, Voice):
            return dumps({'id': resource.id, 'subpart_id': resource.subpart_id}, sort_keys=True)
        else:
            raise TypeError('Resource has wrong Type ' + str(type(resource)))

    @classmethod
    def isOwner(cls, resource, user: [str, User]=None):
        if user is None:
            user = get_jwt_identity()
        if isinstance(user, str):
            user = User.get_user_by_name(user)
        if user is None:
            return False
        type = TypeEnum.fromResource(resource)
        resource_id = History.fingerprint(resource)
        result = cls.query.filter(cls.user == user, cls.method == MethodEnum.create, cls.type == type, cls.resource == resource_id).first()
        return result is not None

    @property
    def full_resource(self) -> Union[Person, Opus, Part, SubPart, Voice, None]:
        if self._full_resource is not None:
            return self._full_resource
        if not self.resource:
            return None
        resource = loads(self.resource)
        if self.type == TypeEnum.person:
            self._full_resource = Person.get_by_id_or_dict(resource, lazy=True)
        elif self.type == TypeEnum.opus:
            self._full_resource = Opus.get_by_id_or_dict(resource, lazy=True)
        elif self.type == TypeEnum.part:
            self._full_resource = Part.get_by_id_or_dict(resource, lazy=True)
        elif self.type == TypeEnum.subpart:
            self._full_resource = SubPart.get_by_id_or_dict(resource, lazy=True)
        elif self.type == TypeEnum.voice:
            self._full_resource = Voice.get_by_id_or_dict(resource, lazy=True)
        else:
            return None
        return self._full_resource


class Backup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, server_default=func.now())
    type = db.Column(db.Enum(TypeEnum))
    resource = db.Column(db.Text())

    def __init__(self, resource_type: TypeEnum, resource: str):
        self.type = resource_type
        self.resource = resource
