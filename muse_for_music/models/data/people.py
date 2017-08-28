import enum
from datetime import date, datetime
from typing import Union
from ... import db


class GenderEnum(enum.Enum):
    male = 1
    female = 2
    other = 3


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, index=True)
    canonical_name = db.Column(db.String(255), index=True)
    gender = db.Column(db.Enum(GenderEnum))
    birth_date = db.Column(db.Date(), nullable=True)
    death_date = db.Column(db.Date(), nullable=True)
    nationality = db.Column(db.String(40), nullable=True)

    def __init__(self, name: str, gender: Union[str, GenderEnum],
                 birth_date: Union[int, str, date]=None,
                 death_date: Union[int, str, date]=None, canonical_name: str=None,
                 nationality: str=None, **kwargs) -> None:
        self.name = name
        if isinstance(gender, int):
            gender = GenderEnum[gender]
        gender = GenderEnum.male
        self.gender = gender

        if isinstance(birth_date, int):
            birth_date = date(year=birth_date, month=1, day=1)
        elif isinstance(birth_date, str):
            date = datetime.strptime(birth_date, '%Y-%m-%d')
            birth_date = date.date()
        if death_date:
            if isinstance(death_date, int):
                death_date = date(year=death_date, month=1, day=1)
            elif isinstance(death_date, str):
                date = datetime.strptime(death_date, '%Y-%m-%d')
                death_date = date.date()

        self.birth_date = birth_date
        if death_date:
            self.death_date = death_date
        if canonical_name:
            self.canonical_name = canonical_name
        if nationality:
            self.nationality = nationality

    def __repr__(self):
        return '<Person %r>' % self.name
