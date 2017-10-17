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
    'id': fields.Integer(readonly=True, example=1),
    '_links': NestedFields(person_links),
})



opus_links = api.inherit('OpusLinks', with_curies, {
    'self': HaLUrl(UrlData('api.opus_opus_resource', absolute=True, url_data={'id': 'id'}),
                   required=False),
    'find': HaLUrl(UrlData('api.opus_opus_list_resource', absolute=True,
                           templated=True, path_variables=['id']), required=False),
    'person': HaLUrl(UrlData('api.person_person_resource', absolute=True,
                             url_data={'id': 'composer.id'}), required=False),
})

opus_post = api.model('OpusPOST', {
    'name': fields.String(required=True, example='duett in g moll'),
    'composer': fields.Nested(person_post, required=True),
})

opus_get_citation = api.inherit('OpusGETCitation', opus_post, {
    'id': fields.Integer(readonly=True, example=1),
    '_links': NestedFields(opus_links),
    'original_name': fields.String(required=True),
    'opus_name': fields.String(required=True),
    'score_link': fields.String(required=True, description='A url linking to the sheet music.'),
    'composition_year': fields.Integer(required=True),
})

instrumentation_context_put = api.model('InstrumentationContextPUT', {
    'id': fields.Integer(readonly=True, example=1),
    'instrumentation_quantity_before': fields.Nested(taxonomy_item_put),
    'instrumentation_quantity_after': fields.Nested(taxonomy_item_put),
    'instrumentation_quality_before': fields.Nested(taxonomy_item_put),
    'instrumentation_quality_after': fields.Nested(taxonomy_item_put),
})

instrumentation_context_get = api.model('InstrumentationContextGET', {
    'id': fields.Integer(readonly=True, example=1),
    'instrumentation_quantity_before': fields.Nested(taxonomy_item_get),
    'instrumentation_quantity_after': fields.Nested(taxonomy_item_get),
    'instrumentation_quality_before': fields.Nested(taxonomy_item_get),
    'instrumentation_quality_after': fields.Nested(taxonomy_item_get),
})

dynamic_context_put = api.model('DynamicContextPUT', {
    'id': fields.Integer(readonly=True, example=1),
    'loudness_before': fields.Nested(taxonomy_item_put),
    'loudness_after': fields.Nested(taxonomy_item_put),
    'dynamic_trend_before': fields.Nested(taxonomy_item_put),
    'dynamic_trend_after': fields.Nested(taxonomy_item_put),
})

dynamic_context_get = api.model('DynamicContextGET', {
    'id': fields.Integer(readonly=True, example=1),
    'loudness_before': fields.Nested(taxonomy_item_get),
    'loudness_after': fields.Nested(taxonomy_item_get),
    'dynamic_trend_before': fields.Nested(taxonomy_item_get),
    'dynamic_trend_after': fields.Nested(taxonomy_item_get),
})

tempo_context_put = api.model('TempoContextPUT', {
    'id': fields.Integer(readonly=True, example=1),
    'tempo_context_before': fields.Nested(taxonomy_item_put),
    'tempo_context_after': fields.Nested(taxonomy_item_put),
    'tempo_trend_before': fields.Nested(taxonomy_item_put),
    'tempo_trend_after': fields.Nested(taxonomy_item_put),
})

tempo_context_get = api.model('TempoContextGET', {
    'id': fields.Integer(readonly=True, example=1),
    'tempo_context_before': fields.Nested(taxonomy_item_get),
    'tempo_context_after': fields.Nested(taxonomy_item_get),
    'tempo_trend_before': fields.Nested(taxonomy_item_get),
    'tempo_trend_after': fields.Nested(taxonomy_item_get),
})

form_put = api.model('FormPUT', {
    'id': fields.Integer(readonly=True, example=1),
    'contains_theme': fields.Boolean(default=True),
    'form_schema': fields.Nested(taxonomy_item_put, description='Formschema'),
    'formal_function': fields.Nested(taxonomy_item_put, description='FormaleFunktion'),
})

form_get = api.model('FormGET', {
    'id': fields.Integer(readonly=True, example=1),
    'contains_theme': fields.Boolean(default=True),
    'form_schema': fields.Nested(taxonomy_item_get, description='Formschema'),
    'formal_function': fields.Nested(taxonomy_item_get, description='FormaleFunktion'),
})

harmonic_center_put = api.model('HarmonicCenterPUT', {
    'id': fields.Integer(readonly=True, example=1),
    'tonalitaet': fields.Nested(taxonomy_item_put, description='Tonalitaet'),
    'harmonische_funktion': fields.Nested(taxonomy_item_put, description='HarmonischeFunktion'),
    'grundton': fields.Nested(taxonomy_item_put, description='Grundton'),
    'harmonische_stufe': fields.Nested(taxonomy_item_put, description='HarmonischeStufe'),
})

harmonic_center_get = api.model('HarmonicCenterGET', {
    'id': fields.Integer(readonly=True, example=1),
    'tonalitaet': fields.Nested(taxonomy_item_get, description='Tonalitaet'),
    'harmonische_funktion': fields.Nested(taxonomy_item_get, description='HarmonischeFunktion'),
    'grundton': fields.Nested(taxonomy_item_get, description='Grundton'),
    'harmonische_stufe': fields.Nested(taxonomy_item_get, description='HarmonischeStufe'),
})

harmonics_put = api.model('HarmonicsPUT', {
    'id': fields.Integer(readonly=True, example=1),
    'degree_of_dissonance': fields.Nested(taxonomy_item_put, description='Dissonanzgrad'),
    'dissonances': fields.List(fields.Nested(taxonomy_item_put, description='Dissonanzen')),
    'harmonic_complexity': fields.Nested(taxonomy_item_put, description='HarmonischeKomplexitaet'),
    'nr_of_different_chords_per_measure': fields.Float(),
    'harmonic_density': fields.Nested(taxonomy_item_put, description='HarmonischeDichte'),
    'nr_of_melody_tones_per_harmony': fields.Float(),
    'melody_tones_in_melody_one_id': fields.Nested(taxonomy_item_put, description='AnzahlMelodietoene'),
    'melody_tones_in_melody_two_id': fields.Nested(taxonomy_item_put, description='AnzahlMelodietoene'),
    'harmonic_phenomenons': fields.List(fields.Nested(taxonomy_item_put, description='HarmonischePhaenomene')),
    'harmonic_changes': fields.List(fields.Nested(taxonomy_item_put, description='HarmonischeEntwicklung')),
    'harmonische_funktion': fields.Nested(taxonomy_item_put, description='HarmonischeFunktionVerwandschaft'),
    'harmonic_centers': fields.List(fields.Nested(harmonic_center_put, description='HarmonicCenter')),
})

harmonics_get = api.model('HarmonicsGET', {
    'id': fields.Integer(readonly=True, example=1),
    'degree_of_dissonance': fields.Nested(taxonomy_item_get, description='Dissonanzgrad'),
    'dissonances': fields.List(fields.Nested(taxonomy_item_get, description='Dissonanzen')),
    'harmonic_complexity': fields.Nested(taxonomy_item_get, description='HarmonischeKomplexitaet'),
    'nr_of_different_chords_per_measure': fields.Float(),
    'harmonic_density': fields.Nested(taxonomy_item_get, description='HarmonischeDichte'),
    'nr_of_melody_tones_per_harmony': fields.Float(),
    'melody_tones_in_melody_one_id': fields.Nested(taxonomy_item_get, description='AnzahlMelodietoene'),
    'melody_tones_in_melody_two_id': fields.Nested(taxonomy_item_get, description='AnzahlMelodietoene'),
    'harmonic_phenomenons': fields.List(fields.Nested(taxonomy_item_get, description='HarmonischePhaenomene')),
    'harmonic_changes': fields.List(fields.Nested(taxonomy_item_get, description='HarmonischeEntwicklung')),
    'harmonische_funktion': fields.Nested(taxonomy_item_get, description='HarmonischeFunktionVerwandschaft'),
    'harmonic_centers': fields.List(fields.Nested(harmonic_center_get, description='HarmonicCenter')),
})

dramaturgic_context_put = api.model('DramaturgicContextPUT', {
    'id': fields.Integer(readonly=True, example=1),
    'ambitus_context_after': fields.Nested(taxonomy_item_put, description='AmbitusEinbettung'),
    'melodic_line_before': fields.Nested(taxonomy_item_put, description='Melodiebewegung'),
    'ambitus_change_after': fields.Nested(taxonomy_item_put, description='AmbitusEntwicklung'),
    'ambitus_context_before': fields.Nested(taxonomy_item_put, description='AmbitusEinbettung'),
    'ambitus_change_before': fields.Nested(taxonomy_item_put, description='AmbitusEntwicklung'),
    'melodic_line_after': fields.Nested(taxonomy_item_put, description='Melodiebewegung'),
})

dramaturgic_context_get = api.model('DramaturgicContextGET', {
    'id': fields.Integer(readonly=True, example=1),
    'ambitus_context_after': fields.Nested(taxonomy_item_get, description='AmbitusEinbettung'),
    'melodic_line_before': fields.Nested(taxonomy_item_get, description='Melodiebewegung'),
    'ambitus_change_after': fields.Nested(taxonomy_item_get, description='AmbitusEntwicklung'),
    'ambitus_context_before': fields.Nested(taxonomy_item_get, description='AmbitusEinbettung'),
    'ambitus_change_before': fields.Nested(taxonomy_item_get, description='AmbitusEntwicklung'),
    'melodic_line_after': fields.Nested(taxonomy_item_get, description='Melodiebewegung'),
})

rhythm_put = api.model('RhythmPUT', {
    'id': fields.Integer(readonly=True, example=1),
    'measure_times': fields.List(fields.Nested(taxonomy_item_put, description='Taktart')),
    'rythmic_phenomenons': fields.List(fields.Nested(taxonomy_item_put, description='RhythmischesPhaenomen')),
    'rythm_types': fields.List(fields.Nested(taxonomy_item_put, description='Rhythmustyp')),
    'polymetric': fields.Boolean(default=False),
})

rhythm_get = api.model('RhythmGET', {
    'id': fields.Integer(readonly=True, example=1),
    'measure_times': fields.List(fields.Nested(taxonomy_item_get, description='Taktart')),
    'rythmic_phenomenons': fields.List(fields.Nested(taxonomy_item_get, description='RhythmischesPhaenomen')),
    'rythm_types': fields.List(fields.Nested(taxonomy_item_get, description='Rhythmustyp')),
    'polymetric': fields.Boolean(default=False),
})

dynamic_marking_put = api.model('DynamicMarkingPUT', {
    'id': fields.Integer(readonly=True, example=1),
    'lautstaerke_zusatz': fields.Nested(taxonomy_item_put, description='LautstaerkeZusatz'),
    'lautstaerke': fields.Nested(taxonomy_item_put, description='Lautstaerke'),
})

dynamic_marking_get = api.model('DynamicMarkingGET', {
    'id': fields.Integer(readonly=True, example=1),
    'lautstaerke_zusatz': fields.Nested(taxonomy_item_get, description='LautstaerkeZusatz'),
    'lautstaerke': fields.Nested(taxonomy_item_get, description='Lautstaerke'),
})

dynamic_put = api.model('DynamicPUT', {
    'id': fields.Integer(readonly=True, example=1),
    'dynamic_changes': fields.List(fields.Nested(taxonomy_item_put, description='LautstaerkeEntwicklung')),
    'dynamic_markings': fields.List(fields.Nested(dynamic_marking_put, description='DynamicMarking')),
})

dynamic_get = api.model('DynamicGET', {
    'id': fields.Integer(readonly=True, example=1),
    'dynamic_changes': fields.List(fields.Nested(taxonomy_item_get, description='LautstaerkeEntwicklung')),
    'dynamic_markings': fields.List(fields.Nested(dynamic_marking_get, description='DynamicMarking')),
})

satz_put = api.model('SatzPUT', {
    'id': fields.Integer(readonly=True, example=1),
    'satzart_allgemein': fields.Nested(taxonomy_item_put, description='SatzartAllgemein'),
    'satzart_speziell': fields.Nested(taxonomy_item_put, description='SatzartSpeziell'),
})

satz_get = api.model('SatzGET', {
    'id': fields.Integer(readonly=True, example=1),
    'satzart_allgemein': fields.Nested(taxonomy_item_get, description='SatzartAllgemein'),
    'satzart_speziell': fields.Nested(taxonomy_item_get, description='SatzartSpeziell'),
})

musicial_sequence_put = api.model('MusicialSequencePUT', {
    'id': fields.Integer(readonly=True, example=1),
    'beats': fields.Integer(),
    'flow': fields.Nested(taxonomy_item_put, description='BewegungImTonraum'),
    'tonal_corrected': fields.Boolean(default=False),
    'starting_interval': fields.Nested(taxonomy_item_put, description='Intervall'),
})

musicial_sequence_get = api.model('MusicialSequenceGET', {
    'id': fields.Integer(readonly=True, example=1),
    'beats': fields.Integer(),
    'flow': fields.Nested(taxonomy_item_get, description='BewegungImTonraum'),
    'tonal_corrected': fields.Boolean(default=False),
    'starting_interval': fields.Nested(taxonomy_item_get, description='Intervall'),
})

composition_put = api.model('CompositionPUT', {
    'id': fields.Integer(readonly=True, example=1),
    'sequences': fields.List(fields.Nested(musicial_sequence_put, description='MusicialSequence')),
    'nr_varied_repetitions': fields.Integer(),
    'nr_exact_repetitions': fields.Integer(),
})

composition_get = api.model('CompositionGET', {
    'id': fields.Integer(readonly=True, example=1),
    'sequences': fields.List(fields.Nested(musicial_sequence_get, description='MusicialSequence')),
    'nr_varied_repetitions': fields.Integer(),
    'nr_exact_repetitions': fields.Integer(),
})

opus_citation_put = api.model('OpusCitationPUT', {
    'id': fields.Integer(readonly=True, example=1),
    'opus': fields.Nested(opus_get_citation, description='Opus'),
    'citation_type': fields.Nested(taxonomy_item_put, description='Zitat'),
})

opus_citation_get = api.model('OpusCitationGET', {
    'id': fields.Integer(readonly=True, example=1),
    'opus': fields.Nested(opus_get_citation, description='Opus'),
    'citation_type': fields.Nested(taxonomy_item_get, description='Zitat'),
})

other_citation = api.model('OtherCitation', {
    'id': fields.Integer(readonly=True, example=1),
    'citation': fields.String(),
})

citations_put = api.model('CitationsGET', {
    'id': fields.Integer(readonly=True, example=1),
    'is_foreign': fields.Boolean(default=False),
    'opus_citations': fields.List(fields.Nested(opus_citation_put, description='OpusCitation')),
    'other_citations': fields.List(fields.Nested(other_citation)),
    'gattung_citations': fields.List(fields.Nested(taxonomy_item_put, description='Gattung')),
    'instrument_citations': fields.List(fields.Nested(taxonomy_item_put, description='Instrument')),
    'program_citations': fields.List(fields.Nested(taxonomy_item_put, description='Programmgegenstand')),
    'tonmalerei_citations': fields.List(fields.Nested(taxonomy_item_put, description='Tonmalerei')),
    'composer_citations': fields.List(fields.Nested(taxonomy_item_put, description='Person')),
    'epoch_citations': fields.List(fields.Nested(taxonomy_item_put, description='Epoche')),
})

citations_get = api.model('CitationsGET', {
    'id': fields.Integer(readonly=True, example=1),
    'is_foreign': fields.Boolean(default=False),
    'opus_citations': fields.List(fields.Nested(opus_citation_get, description='OpusCitation')),
    'other_citations': fields.List(fields.Nested(other_citation)),
    'gattung_citations': fields.List(fields.Nested(taxonomy_item_get, description='Gattung')),
    'instrument_citations': fields.List(fields.Nested(taxonomy_item_get, description='Instrument')),
    'program_citations': fields.List(fields.Nested(taxonomy_item_get, description='Programmgegenstand')),
    'tonmalerei_citations': fields.List(fields.Nested(taxonomy_item_get, description='Tonmalerei')),
    'composer_citations': fields.List(fields.Nested(taxonomy_item_get, description='Person')),
    'epoch_citations': fields.List(fields.Nested(taxonomy_item_get, description='Epoche')),
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
    'measure_start': fields.Nested(measure_model, required=True),
    'measure_end': fields.Nested(measure_model, required=True),
    'length': fields.Integer(min=1, required=True, example=1),
    'occurence_in_movement': fields.Nested(taxonomy_item_put, required=True),
})

part_put = api.inherit('PartPUT', part_post, {
    'instrumentation_context': fields.Nested(instrumentation_context_put, required=True),
    'dynamic_context': fields.Nested(dynamic_context_put, required=True),
    'tempo_context': fields.Nested(tempo_context_put, required=True),
    'form': fields.Nested(form_put, required=True),
})

subpart_links = api.inherit('SubPartLinks', with_curies, {
    'self': HaLUrl(UrlData('api.subpart_sub_part_resource', absolute=True,
                           url_data={'part_id': 'part_id', 'subpart_id':'id'}), rquired=False),
})

subpart_post = api.model('SubPartPOST', {
    'label': fields.String(pattern='^[A-Z]\'{0,4}$', required=True, max_length=5),
})

subpart_put = api.inherit('SubPartPUT', subpart_post, {
    'id': fields.Integer(readonly=True, example=1),
    'label': fields.String(required=True, default='A'),
    'occurence_in_part': fields.Nested(taxonomy_item_put, required=True, description='Anteil'),
    'instrumentation': fields.List(fields.Nested(taxonomy_item_put, required=True, description='Instrument')),
    'instrumentation_context': fields.Nested(instrumentation_context_put, required=True),
    'composition': fields.Nested(composition_put, required=True, description='Composition'),
    'rythm': fields.Nested(rhythm_put, required=True, description='Rythm'),
    'dramaturgic_context': fields.Nested(dramaturgic_context_put, required=True, description='DramaturgicContext'),
    'satz': fields.Nested(satz_put, required=True, description='Satz'),
    'dynamic_context': fields.Nested(dynamic_context_put, required=True, description='DynamicContext'),
    'harmonics': fields.Nested(harmonics_put, required=True, description='Harmonics'),
    'form': fields.Nested(form_put, required=True, description='Form'),
    'dynamic': fields.Nested(dynamic_put, required=True, description='Dynamic'),
    'citations': fields.Nested(citations_put, description='Citations'),
})

subpart_get = api.inherit('SubPartGET', subpart_put, {
    'id': fields.Integer(readonly=True, example=1),
    'part_id': fields.Integer(readonly=True, example=1),
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
    'citations': fields.Nested(citations_get, description='Citations'),
})

part_get = api.inherit('PartGET', part_put, {
    'id': fields.Integer(required=False, readonly=True, example=1),
    'opus_id': fields.Integer(readonly=True, example=1),
    '_links': NestedFields(part_links),
    'occurence_in_movement': fields.Nested(taxonomy_item_get),
    'instrumentation_context': fields.Nested(instrumentation_context_get),
    'dynamic_context': fields.Nested(dynamic_context_get),
    'tempo_context': fields.Nested(tempo_context_get),
    'form': fields.Nested(form_get),
    'subparts': fields.List(fields.Nested(subpart_get), default=[]),
})

opus_put = api.inherit('OpusPUT', opus_post, {
    'original_name': fields.String(required=True),
    'opus_name': fields.String(required=True),
    'score_link': fields.String(required=True, description='A url linking to the sheet music.'),
    'composition_year': fields.Integer(required=True),
    'composition_place': fields.String(required=True, example='TODO'),
    'instrumentation': fields.List(fields.Nested(taxonomy_item_get), required=True, default=[]),
    'occasion': fields.String(required=True),
    'dedication': fields.String(required=True),
    'notes': fields.String(required=True),
    'printed': fields.Boolean(required=True, default=False),
    'first_printed_at': fields.String(required=True, example='TODO'),
    'first_printed_in': fields.Integer(required=True),
    'publisher': fields.String(required=True),
    'movements': fields.Integer(required=True, default=1),
    'genre': fields.String(required=True),
})

opus_get = api.inherit('OpusGET', opus_put, {
    'id': fields.Integer(readonly=True, example=1),
    '_links': NestedFields(opus_links),
    'composer': fields.Nested(person_get),
    'instrumentation': fields.List(fields.Nested(taxonomy_item_get), required=True),
    'parts': fields.List(fields.Nested(part_get), default=[]),
})
