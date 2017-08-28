"""
Models for data objects.
"""


from flask_restplus import fields
from ...hal_field import HaLUrl, NestedFields, EmbeddedFields, NestedModel, UrlData
from . import api
from ..models import with_curies

from enum import Enum
from datetime import datetime, date


def parse_date(date_str: str) -> date:
    parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
    return parsed_date.date()


data_links = api.inherit('DataLinks', with_curies, {
    'self': HaLUrl(UrlData('api.data_data_resource', absolute=True)),
    'rel:person': HaLUrl(UrlData('api.person_person_list_resource', absolute=True)),
    'rel:opus': HaLUrl(UrlData('api.opus_opus_list_resource', absolute=True)),
    'rel:instrumentation': HaLUrl(UrlData('api.instrumentation_instrumentation_list_resource', absolute=True)),
})

data_model = api.model('DataModel', {
    '_links': NestedFields(data_links),
})


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
    'self': HaLUrl(UrlData('api.person_person_resource', absolute=True, url_data={'id': 'id'}),
                   required=False),
    'find': HaLUrl(UrlData('api.person_person_list_resource', absolute=True, templated=True,
                           path_variables=['id']), required=False),
})

person_post = api.model('PersonPOST', {
    'name': fields.String(required=True, example='admin'),
    'gender': GenderField(required=True, example='male', enum=['male', 'female', 'other'])
})

person_put = api.inherit('PersonPUSH', person_post, {
    'canonical_name': fields.String(required=False, example='admin'),
    'birth_date': fields.Date(required=False, example='1921-2-4'),
    'death_date': fields.Date(required=False, example='1921-3-23'),
})

person_get = api.inherit('PersonGET', person_put, {
    'id': fields.Integer(required=False, readonly=True),
    '_links': NestedFields(person_links),
})

instrumentation_links = api.model('InstrumentationLinks', {
    'self': HaLUrl(UrlData('api.instrumentation_instrumentation_resource', absolute=True,
                           url_data={'id': 'id'}), required=False),
})

instrumentation_model = api.model('Instrumentation', {
    'id': fields.Integer(required=False, readonly=True),
    '_links': NestedFields(instrumentation_links),
    'instruments': fields.List(fields.String(), required=True),
})

opus_links = api.inherit('OpusLinks', with_curies, {
    'self': HaLUrl(UrlData('api.opus_opus_resource', absolute=True, url_data={'id': 'id'}),
                   required=False),
    'find': HaLUrl(UrlData('api.opus_opus_list_resource', absolute=True,
                           templated=True, path_variables=['id']), required=False),
    'rel:person': HaLUrl(UrlData('api.person_person_resource', absolute=True,
                                 url_data={'id': 'composer.id'}), required=False),
    'rel:instrumentation': HaLUrl(UrlData('api.instrumentation_instrumentation_resource',
                                          absolute=True, url_data={'id': 'instrumentation.id'}),
                                  required=False),
})


opus_post = api.model('OpusPOST', {
    'name': fields.String(required=True, example='duett in g moll'),
})

opus_put = api.inherit('OpusPUSH', opus_post, {
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

opus_get = api.inherit('OpusGET', opus_put, {
    'id': fields.Integer(required=False, readonly=True),
    '_links': NestedFields(opus_links),
    '_embedded': EmbeddedFields({
        'instrumentation': NestedModel(instrumentation_model),
        'person': NestedModel(person_get, attribute='composer'),
    }, required=True),
})
