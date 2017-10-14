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

form_put = api.model('FormPUT', {
    'id': fields.Integer(),
    'contains_theme': fields.Boolean(default=True),
    'form_schema': fields.Nested(taxonomy_item_put, description='Formschema'),
    'formal_function': fields.Nested(taxonomy_item_put, description='FormaleFunktion'),
})

form_get = api.model('FormGET', {
    'id': fields.Integer(),
    'contains_theme': fields.Boolean(default=True),
    'form_schema': fields.Nested(taxonomy_item_get, description='Formschema'),
    'formal_function': fields.Nested(taxonomy_item_get, description='FormaleFunktion'),
})

harmonic_center_get = api.model('HarmonicCenterGET', {
    'id': fields.Integer(),
    'tonalitaet': fields.Nested(taxonomy_item_get, description='Tonalitaet'),
    'harmonische_funktion': fields.Nested(taxonomy_item_get, description='HarmonischeFunktion'),
    'grundton': fields.Nested(taxonomy_item_get, description='Grundton'),
    'harmonische_stufe': fields.Nested(taxonomy_item_get, description='HarmonischeStufe'),
})

harmonics_get = api.model('HarmonicsGET', {
    'id': fields.Integer(),
    'degree_of_dissonance': fields.Nested(taxonomy_item_get, description='Dissonanzgrad'),
    'dissonances': fields.List(fields.Nested(taxonomy_item_get, description='Dissonanzen')),
    'harmonic_complexity': fields.Nested(taxonomy_item_get, description='HarmonischeKomplexitaet'),
    'nr_of_different_chords_per_measure': fields.Float(),
    'frequence_of_harmony_change': fields.Nested(taxonomy_item_get, description='Frequenz'),
    'harmonic_phenomenons': fields.List(fields.Nested(taxonomy_item_get, description='HarmonischePhaenomene')),
    'harmonic_changes': fields.List(fields.Nested(taxonomy_item_get, description='HarmonischeEntwicklung')),
    'harmonische_funktion': fields.Nested(taxonomy_item_get, description='HarmonischeFunktionVerwandschaft'),
    'harmonic_centers': fields.List(fields.Nested(harmonic_center_get, description='HarmonicCenter')),
})

dramaturgic_context_get = api.model('DramaturgicContextGET', {
    'id': fields.Integer(),
    'ambitus_context_after': fields.Nested(taxonomy_item_get, description='AmbitusEinbettung'),
    'melodic_line_before': fields.Nested(taxonomy_item_get, description='Melodiebewegung'),
    'ambitus_change_after': fields.Nested(taxonomy_item_get, description='AmbitusEntwicklung'),
    'ambitus_context_before': fields.Nested(taxonomy_item_get, description='AmbitusEinbettung'),
    'ambitus_change_before': fields.Nested(taxonomy_item_get, description='AmbitusEntwicklung'),
    'melodic_line_after': fields.Nested(taxonomy_item_get, description='Melodiebewegung'),
})

rhythm_get = api.model('RhythmGET', {
    'id': fields.Integer(),
    'measure_times': fields.List(fields.Nested(taxonomy_item_get, description='Taktart')),
    'rythmic_phenomenons': fields.List(fields.Nested(taxonomy_item_get, description='RhythmischesPhaenomen')),
    'rythm_types': fields.List(fields.Nested(taxonomy_item_get, description='Rhythmustyp')),
    'polymetric': fields.Boolean(default=False),
})

dynamic_marking_get = api.model('DynamicMarkingGET', {
    'id': fields.Integer(),
    'lautstaerke_zusatz': fields.Nested(taxonomy_item_get, description='LautstaerkeZusatz'),
    'lautstaerke': fields.Nested(taxonomy_item_get, description='Lautstaerke'),
})

dynamic_get = api.model('DynamicGET', {
    'id': fields.Integer(),
    'dynamic_changes': fields.List(fields.Nested(taxonomy_item_get, description='LautstaerkeEntwicklung')),
    'dynamic_markings': fields.List(fields.Nested(dynamic_marking_get, description='DynamicMarking')),
})

satz_get = api.model('SatzGET', {
    'id': fields.Integer(),
    'satzart_allgemein': fields.Nested(taxonomy_item_get, description='SatzartAllgemein'),
    'satzart_speziell': fields.Nested(taxonomy_item_get, description='SatzartSpeziell'),
})

musicial_sequence_get = api.model('MusicialSequenceGET', {
    'id': fields.Integer(),
    'beats': fields.Integer(),
    'flow': fields.Nested(taxonomy_item_get, description='BewegungImTonraum'),
    'tonal_corrected': fields.Boolean(default=False),
    'starting_interval': fields.Nested(taxonomy_item_get, description='Intervall'),
})

composition_get = api.model('CompositionGET', {
    'id': fields.Integer(),
    'sequences': fields.List(fields.Nested(musicial_sequence_get, description='MusicialSequence')),
    'nr_varied_repetitions': fields.Integer(),
    'nr_exact_repetitions': fields.Integer(),
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
    'length': fields.Integer(min=1),
    'occurence_in_movement': fields.Nested(taxonomy_item_put),
})

part_put = api.inherit('PartPUT', part_post, {
    'instrumentation_context': fields.Nested(instrumentation_context_put),
    'dynamic_context': fields.Nested(dynamic_context_put),
    'tempo_context': fields.Nested(tempo_context_put),
    'form': fields.Nested(form_put),
})

subpart_links = api.inherit('SubPartLinks', with_curies, {
    'self': HaLUrl(UrlData('api.subpart_sub_part_resource', absolute=True,
                           url_data={'part_id': 'part_id', 'subpart_id':'id'}), rquired=False),
})

subpart_post = api.model('SubPartPOST', {
    'part_id': fields.Integer(),
    'label': fields.String(pattern='^[A-Z]\'{0,4}$', max_length=5),
})

subpart_put = api.inherit('SubPartPUT', subpart_post, {
    'id': fields.Integer(),
    'label': fields.String(default='A'),
    'occurence_in_part': fields.Nested(taxonomy_item_put, description='Anteil'),
    'instrumentation': fields.List(fields.Nested(taxonomy_item_put, description='Instrument')),
    'instrumentation_context': fields.Nested(instrumentation_context_put),
})

subpart_get = api.inherit('SubPartGET', subpart_put, {
    'id': fields.Integer(required=False, readonly=True),
    '_links': NestedFields(subpart_links),
    'occurence_in_part': fields.Nested(taxonomy_item_get, description='Anteil'),
    'instrumentation': fields.List(fields.Nested(taxonomy_item_get, description='Instrument')),
    'instrumentation_context': fields.Nested(instrumentation_context_get),
    'composition': fields.Nested(composition_get, description='Composition'),
    'rythm': fields.Nested(rhythm_get, description='Rythm'),
    'dramaturgic_context': fields.Nested(dramaturgic_context_get, description='DramaturgicContext'),
    'satz': fields.Nested(satz_get, description='Satz'),
    'dynamic_context': fields.Nested(dynamic_context_get, description='DynamicContext'),
    'harmonics': fields.Nested(harmonics_get, description='Harmonics'),
    'form': fields.Nested(form_get, description='Form'),
    'dynamic': fields.Nested(dynamic_get, description='Dynamic'),
})

part_get = api.inherit('PartGET', part_put, {
    'id': fields.Integer(required=False, readonly=True),
    '_links': NestedFields(part_links),
    'occurence_in_movement': fields.Nested(taxonomy_item_get),
    'instrumentation_context': fields.Nested(instrumentation_context_get),
    'dynamic_context': fields.Nested(dynamic_context_get),
    'tempo_context': fields.Nested(tempo_context_get),
    'form': fields.Nested(form_get),
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
