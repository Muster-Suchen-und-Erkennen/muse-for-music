"""
Models for data objects.
"""


from flask_restplus import fields
from . import ns

from enum import Enum


class GenderField(fields.Raw, fields.StringMixin):
    __schema_type__ = 'string'

    def __init__(self, *args, **kwargs):
        self.enum = kwargs.pop('enum', None)
        self.discriminator = kwargs.pop('discriminator', None)
        super().__init__(*args, **kwargs)
        self.required = self.discriminator or self.required

    def format(self, value: Enum):
        if not isinstance(value, Enum):
            raise fields.MarshallingError('Gender field used for wrong field.')
        return value.name

    def schema(self):
        enum = self._v('enum')
        schema = super().schema()
        schema.update(enum=enum)
        if enum and schema['example'] is None:
            schema['example'] = enum[0]
        return schema


person_model = ns.model('Person', {
    'id': fields.Integer(required=False, readonly=True),
    'url': fields.Url('api.data_person_resource', absolute=True, required=False, readonly=True),
    'name': fields.String(required=True, example='admin'),
    'canonical_name': fields.String(required=False, example='admin'),
    'birth_date': fields.Date(required=True, example='1921-2-4'),
    'death_date': fields.Date(required=False, example='1921-3-23'),
    'gender': GenderField(required=True, example='male', enum=['male', 'female', 'other'])
})

instrumentation_model = ns.model('Instrumentation', {
    'id': fields.Integer(required=False, readonly=True),
    'url': fields.Url('api.data_instrumentation_resource', absolute=True, required=False, readonly=True),
    'instruments': fields.List(fields.String(), required=True),
})

opus_model = ns.model('Opus', {
    'id': fields.Integer(required=False, readonly=True),
    'url': fields.Url('api.data_opus_resource', absolute=True, required=False, readonly=True),
    'name': fields.String(required=True, example='duett in g moll'),
    'original_name': fields.String(required=False),
    'opus_name': fields.String(required=False),
    'composer': fields.Nested(person_model, allow_null=True),
    'composition_year': fields.Integer(required=False),
    'composition_place': fields.String(required=False, example='TODO'),
    'occasion': fields.String(required=False),
    'dedication': fields.String(required=False),
    'notes': fields.String(required=False),
    'printed': fields.Boolean(required=False, default=False),
    'first_printed_at': fields.String(required=False, example='TODO'),
    'first_printed_in': fields.Integer(required=False),
    'publisher': fields.String(required=False),
    'instrumentation': fields.Nested(instrumentation_model, required=False),
    'movements': fields.Integer(required=True, default=1),
    'genre': fields.String(required=False),
})
