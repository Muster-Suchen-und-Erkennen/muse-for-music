import enum
from datetime import date, datetime
from typing import Union
from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin


class GenderEnum(enum.Enum):
    male = 1
    female = 2
    other = 3


class Person(db.Model, GetByID, UpdateableModelMixin):

    _normal_attributes = (('name', str),
                          ('gender', str),
                          ('birth_date', int),
                          ('death_date', int),
                          ('nationality', str))


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(191), unique=True, index=True)
    gender = db.Column(db.Enum(GenderEnum))
    birth_date = db.Column(db.Integer(), nullable=True)
    death_date = db.Column(db.Integer(), nullable=True)
    nationality = db.Column(db.String(100), nullable=True)

    def __init__(self, name: str, gender: Union[str, GenderEnum],
                 birth_date: int = -1,
                 death_date: int = -1,
                 nationality: str=None, **kwargs) -> None:
        self.name = name
        if isinstance(gender, int):
            gender = GenderEnum[gender]
        gender = GenderEnum.male
        self.gender = gender

        self.birth_date = birth_date if birth_date > 0 else None
        self.death_date = death_date if death_date > 0 else None

        if nationality:
            self.nationality = nationality

    def __repr__(self):
        return '<Person %r>' % self.name
