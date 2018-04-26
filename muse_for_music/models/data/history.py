import enum
from typing import Union, Sequence

from ... import db


class TypeEnum(enum.Enum):
    person = 1
    opus = 2
    part = 3
    subpart = 4
    voice = 5


class History(db.Model):
    time = db.Column(db.DateTime, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.Enum(TypeEnum))
    resource = db.Column(db.String())

    def __init__(self, user, type: TypeEnum, resource):
        pass
