"""
Models for data objects.
"""


from flask_restplus import fields
from . import ns

from enum import Enum


class GenderField(fields.Raw):
    __schema_type__ = 'GenderEnum'

    def format(self, value: Enum):
        if not isinstance(value, Enum):
            raise fields.MarshallingError('Gender field used for wrong field.')
        return value.name


person_model = ns.model('Person', {
    'name': fields.String(required=True, example='admin'),
    'canonical_name': fields.String(required=False, example='admin'),
    'birth_date': fields.Date(required=True, example=1921),
    'death_date': fields.Date(required=False, example=1921),
    'gender': GenderField(required=True, example='male')
})
