"""
Models for data objects.
"""


from flask_restplus import fields
from ...hal_field import HaLUrl, NestedFields, EmbeddedFields, NestedModel, UrlData
from . import api
from ..models import with_curies
from ..taxonomies.models import taxonomy_item_get, taxonomy_item_put

from enum import Enum
from datetime import datetime, date


def parse_date(date_str: str) -> date:
    parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
    return parsed_date.date()


data_links = api.inherit('DataLinks', with_curies, {
    'self': HaLUrl(UrlData('api.data_data_resource', absolute=True)),
    'person': HaLUrl(UrlData('api.person_person_list_resource', absolute=True)),
    'opus': HaLUrl(UrlData('api.opus_opus_list_resource', absolute=True)),
    'instrumentation': HaLUrl(UrlData('api.instrumentation_instrumentation_list_resource', absolute=True)),
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

person_put = api.inherit('PersonPUT', person_post, {
    'canonical_name': fields.String(example='admin'),
    'birth_date': fields.Date(example='1921-2-4'),
    'death_date': fields.Date(example='1921-3-23'),
})

person_get = api.inherit('PersonGET', person_put, {
    'id': fields.Integer(readonly=True),
    '_links': NestedFields(person_links),
})

instrumentation_links = api.model('InstrumentationLinks', {
    'self': HaLUrl(UrlData('api.instrumentation_instrumentation_resource', absolute=True,
                           url_data={'id': 'id'}), required=False),
})

instrumentation_context_put = api.model('InstrumentationContextPUT', {
    'instrumentation_quantity_before': fields.Nested(taxonomy_item_put),
    'instrumentation_quantity_after': fields.Nested(taxonomy_item_put),
    'instrumentation_quality_before': fields.Nested(taxonomy_item_put),
    'instrumentation_quality_after': fields.Nested(taxonomy_item_put),
})

instrumentation_context_get = api.model('InstrumentationContextGET', {
    'instrumentation_quantity_before': fields.Nested(taxonomy_item_get),
    'instrumentation_quantity_after': fields.Nested(taxonomy_item_get),
    'instrumentation_quality_before': fields.Nested(taxonomy_item_get),
    'instrumentation_quality_after': fields.Nested(taxonomy_item_get),
})

dynamic_context_put = api.model('DynamicContextPUT', {
    'loudness_before': fields.Nested(taxonomy_item_put),
    'loudness_after': fields.Nested(taxonomy_item_put),
    'dynamic_trend_before': fields.Nested(taxonomy_item_put),
    'dynamic_trend_after': fields.Nested(taxonomy_item_put),
})

dynamic_context_get = api.model('DynamicContextGET', {
    'loudness_before': fields.Nested(taxonomy_item_get),
    'loudness_after': fields.Nested(taxonomy_item_get),
    'dynamic_trend_before': fields.Nested(taxonomy_item_get),
    'dynamic_trend_after': fields.Nested(taxonomy_item_get),
})

tempo_context_put = api.model('TempoContextPUT', {
    'tempo_context_before': fields.Nested(taxonomy_item_put),
    'tempo_context_after': fields.Nested(taxonomy_item_put),
    'tempo_trend_before': fields.Nested(taxonomy_item_put),
    'tempo_trend_after': fields.Nested(taxonomy_item_put),
})

tempo_context_get = api.model('TempoContextGET', {
    'tempo_context_before': fields.Nested(taxonomy_item_get),
    'tempo_context_after': fields.Nested(taxonomy_item_get),
    'tempo_trend_before': fields.Nested(taxonomy_item_get),
    'tempo_trend_after': fields.Nested(taxonomy_item_get),
})

measure_model = api.model('Measure', {
    'measure': fields.Integer(min=0, required=True),
    'from_page': fields.Integer(min=0, required=False),
})

part_links = api.inherit('PartLinks', with_curies, {
    'self': HaLUrl(UrlData('api.part_part_resource', absolute=True,
                           url_data={'id': 'id'}), rquired=False),
})

part_post = api.model('PartPOST', {
    'opus_id': fields.Integer(),
    'measure_start': fields.Nested(measure_model),
    'measure_end': fields.Nested(measure_model),
    'occurence_in_movement': fields.Nested(taxonomy_item_put),
})

part_put = api.inherit('PartPUT', part_post, {
    'instrumentation_context': fields.Nested(instrumentation_context_put),
    'dynamic_context': fields.Nested(dynamic_context_put),
    'tempo_context': fields.Nested(tempo_context_put),
})

subpart_links = api.inherit('SubPartLinks', with_curies, {
    #'self': HaLUrl(UrlData('api.part_part_resource', absolute=True,
    #                       url_data={'id': 'id'}), rquired=False),
})

subpart_post = api.model('SubPartPOST', {
    'part_id': fields.Integer(),
    'label': fields.String(pattern='^[A-Z]+$'),
})

subpart_put = api.inherit('SubPartPUT', subpart_post, {

})

subpart_get = api.inherit('SubPartGET', subpart_put, {
    'id': fields.Integer(required=False, readonly=True),
    '_links': NestedFields(subpart_links),
})

part_get = api.inherit('PartGET', part_put, {
    'id': fields.Integer(required=False, readonly=True),
    '_links': NestedFields(part_links),
    'occurence_in_movement': fields.Nested(taxonomy_item_get),
    'instrumentation_context': fields.Nested(instrumentation_context_get),
    'dynamic_context': fields.Nested(dynamic_context_get),
    'tempo_context': fields.Nested(tempo_context_get),
    'subparts': fields.List(fields.Nested(subpart_get), default=[]),
})

opus_links = api.inherit('OpusLinks', with_curies, {
    'self': HaLUrl(UrlData('api.opus_opus_resource', absolute=True, url_data={'id': 'id'}),
                   required=False),
    'find': HaLUrl(UrlData('api.opus_opus_list_resource', absolute=True,
                           templated=True, path_variables=['id']), required=False),
    'person': HaLUrl(UrlData('api.person_person_resource', absolute=True,
                             url_data={'id': 'composer.id'}), required=False),
    'instrumentation': HaLUrl(UrlData('api.instrumentation_instrumentation_resource',
                                      absolute=True, url_data={'id': 'instrumentation.id'}),
                              required=False),
})


opus_post = api.model('OpusPOST', {
    'name': fields.String(required=True, example='duett in g moll'),
    'composer': fields.Nested(person_post),
})

opus_put = api.inherit('OpusPUT', opus_post, {
    'original_name': fields.String(),
    'opus_name': fields.String(),
    'score_link': fields.String(description='A url linking to the sheet music.'),
    'composition_year': fields.Integer(),
    'composition_place': fields.String(example='TODO'),
    'instrumentation': fields.List(fields.Nested(taxonomy_item_get), required=True),
    'occasion': fields.String(),
    'dedication': fields.String(),
    'notes': fields.String(),
    'printed': fields.Boolean(default=False),
    'first_printed_at': fields.String(example='TODO'),
    'first_printed_in': fields.Integer(),
    'publisher': fields.String(),
    'movements': fields.Integer(default=1),
    'genre': fields.String(),
})

opus_get = api.inherit('OpusGET', opus_put, {
    'id': fields.Integer(readonly=True),
    '_links': NestedFields(opus_links),
    'composer': fields.Nested(person_get),
    'instrumentation': fields.List(fields.Nested(taxonomy_item_get), required=True),
    'parts': fields.List(fields.Nested(part_get), default=[]),
})
