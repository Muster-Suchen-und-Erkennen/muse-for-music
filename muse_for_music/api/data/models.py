"""
Models for data objects.
"""


from flask_restplus import fields
from ...hal_field import HaLUrl, NestedFields, EmbeddedFields, NestedModel
from . import api

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


person_links = api.model('PersonLinks', {
    'self': HaLUrl('api.person_person_resource', absolute=True, required=False, data={'id': 'id'}),
    'find': HaLUrl('api.person_person_list_resource', absolute=True, required=False, templated=True, path_variables=['id']),
})

person_model = api.model('Person', {
    'id': fields.Integer(required=False, readonly=True),
    '_links': NestedFields(person_links),
    'name': fields.String(required=True, example='admin'),
    'canonical_name': fields.String(required=False, example='admin'),
    'birth_date': fields.Date(required=True, example='1921-2-4'),
    'death_date': fields.Date(required=False, example='1921-3-23'),
    'gender': GenderField(required=True, example='male', enum=['male', 'female', 'other'])
})

instrumentation_links = api.model('InstrumentationLinks', {
    'self': HaLUrl('api.instrumentation_instrumentation_resource', absolute=True, required=False, data={'id': 'id'}),
})

instrumentation_model = api.model('Instrumentation', {
    'id': fields.Integer(required=False, readonly=True),
    '_links': NestedFields(instrumentation_links),
    'instruments': fields.List(fields.String(), required=True),
})

opus_links = api.model('OpusLinks', {
    'self': HaLUrl('api.opus_opus_resource', absolute=True, required=False, data={'id': 'id'}),
    'find': HaLUrl('api.opus_opus_list_resource', absolute=True, required=False, templated=True, path_variables=['id']),
    'person': HaLUrl('api.person_person_resource', absolute=True, required=False, data={'id': 'composer.id'}),
    'instrumentation': HaLUrl('api.instrumentation_instrumentation_resource', absolute=True, required=False, data={'id': 'instrumentation.id'}),
})

opus_model = api.model('Opus', {
    'id': fields.Integer(required=False, readonly=True),
    '_links': NestedFields(opus_links),
    '_embedded': EmbeddedFields({
        'instrumentation': NestedModel(instrumentation_model),
        'person': NestedModel(person_model, attribute='composer'),
    }, required=True),
    'name': fields.String(required=True, example='duett in g moll'),
    'original_name': fields.String(required=False),
    'opus_name': fields.String(required=False),
    'composer': fields.Integer(attribute='composer.id'),
    'composition_year': fields.Integer(required=False),
    'composition_place': fields.String(required=False, example='TODO'),
    'occasion': fields.String(required=False),
    'dedication': fields.String(required=False),
    'notes': fields.String(required=False),
    'printed': fields.Boolean(required=False, default=False),
    'first_printed_at': fields.String(required=False, example='TODO'),
    'first_printed_in': fields.Integer(required=False),
    'publisher': fields.String(required=False),
    'movements': fields.Integer(required=True, default=1),
    'genre': fields.String(required=False),
})
