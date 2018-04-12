"""Models for data objects."""


from flask_restplus import fields
from ...hal_field import HaLUrl, NestedFields, EmbeddedFields, NestedModel, UrlData
from . import api
from ..models import with_curies
from ..taxonomies.models import taxonomy_item_get, taxonomy_item_put

from enum import Enum
from datetime import datetime, date


def parse_date(date_str: str) -> date:
    """Parse a date string into a date object.

    Arguments:
        date_str: str -- the date string to parse

    Returns:
        date -- the parsed date
    """

    parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
    return parsed_date.date()


class GenderField(fields.Raw, fields.StringMixin):
    """Custom Class for Gender Enum in a field."""

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
    'name': fields.String(title='Name', description='Name der Person', max_length=255, default='', required=True, example='admin'),
    'gender': GenderField(title='Geschlecht', description='Geschlecht der Person', required=True, example='male', enum=['male', 'female', 'other'])
})

person_put = api.inherit('PersonPUT', person_post, {
    'canonical_name': fields.String(title='Kanonischer Name', max_length=255, default='', example='admin'),
    'birth_date': fields.Date(title='Geburtstag', example='1921-2-4'),
    'death_date': fields.Date(title='Todestag', example='1921-3-23'),
})

person_get = api.inherit('PersonGET', person_put, {
    'id': fields.Integer(default=1, readonly=True, example=1),
    '_links': NestedFields(person_links),
})



opus_links = api.inherit('OpusLinks', with_curies, {
    'self': HaLUrl(UrlData('api.opus_opus_resource', absolute=True, url_data={'id': 'id'}),
                   required=False),
    'find': HaLUrl(UrlData('api.opus_opus_list_resource', absolute=True,
                           templated=True, path_variables=['id']), required=False),
    'person': HaLUrl(UrlData('api.person_person_resource', absolute=True,
                             url_data={'id': 'composer.id'}), required=False),
    'part': HaLUrl(UrlData('api.opus_opus_parts_resource', absolute=True,
                            url_data={'id': 'id'}), required=False),
})

opus_post = api.model('OpusPOST', {
    'name': fields.String(max_length=255, default='', required=True, example='duett in g moll', title='Name'),
    'composer': fields.Nested(person_get, description='The composer. {"reference": "person"}', title='Komponist', required=True),
})

opus_get_citation = api.inherit('OpusGETCitation', opus_post, {
    'id': fields.Integer(default=1, readonly=True, example=1),
    '_links': NestedFields(opus_links),
    'original_name': fields.String(default='', required=True),
    'opus_name': fields.String(default='', required=True),
    'score_link': fields.String(default='', required=True, description='A url linking to the sheet music.'),
    'composition_year': fields.Integer(default=1, required=True),
})

instrumentation_context_put = api.model('InstrumentationContextPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'instrumentation_quantity_before': fields.Nested(taxonomy_item_put, description='{"taxonomy": "InstrumentierungEinbettungQuantitaet"}'),
    'instrumentation_quantity_after': fields.Nested(taxonomy_item_put, description='{"taxonomy": "InstrumentierungEinbettungQuantitaet"}'),
    'instrumentation_quality_before': fields.Nested(taxonomy_item_put, description='{"taxonomy": "InstrumentierungEinbettungQualitaet"}'),
    'instrumentation_quality_after': fields.Nested(taxonomy_item_put, description='{"taxonomy": "InstrumentierungEinbettungQualitaet"}'),
})

instrumentation_context_get = api.model('InstrumentationContextGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'instrumentation_quantity_before': fields.Nested(taxonomy_item_get, description='{"taxonomy": "InstrumentierungEinbettungQuantitaet"}'),
    'instrumentation_quantity_after': fields.Nested(taxonomy_item_get, description='{"taxonomy": "InstrumentierungEinbettungQuantitaet"}'),
    'instrumentation_quality_before': fields.Nested(taxonomy_item_get, description='{"taxonomy": "InstrumentierungEinbettungQualitaet"}'),
    'instrumentation_quality_after': fields.Nested(taxonomy_item_get, description='{"taxonomy": "InstrumentierungEinbettungQualitaet"}'),
})

dynamic_context_put = api.model('DynamicContextPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'loudness_before': fields.Nested(taxonomy_item_put, description='{"taxonomy": "Lautstaerke"}'),
    'loudness_after': fields.Nested(taxonomy_item_put, description='{"taxonomy": "Lautstaerke"}'),
    'dynamic_trend_before': fields.Nested(taxonomy_item_put, description='{"taxonomy": "LautstaerkeEinbettung"}'),
    'dynamic_trend_after': fields.Nested(taxonomy_item_put, description='{"taxonomy": "LautstaerkeEinbettung"}'),
})

dynamic_context_get = api.model('DynamicContextGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'loudness_before': fields.Nested(taxonomy_item_get, description='{"taxonomy": "Lautstaerke"}'),
    'loudness_after': fields.Nested(taxonomy_item_get, description='{"taxonomy": "Lautstaerke"}'),
    'dynamic_trend_before': fields.Nested(taxonomy_item_get, description='{"taxonomy": "LautstaerkeEinbettung"}'),
    'dynamic_trend_after': fields.Nested(taxonomy_item_get, description='{"taxonomy": "LautstaerkeEinbettung"}'),
})

tempo_context_put = api.model('TempoContextPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'tempo_context_before': fields.Nested(taxonomy_item_put, description='{"taxonomy": "TempoEinbettung"}'),
    'tempo_context_after': fields.Nested(taxonomy_item_put, description='{"taxonomy": "TempoEinbettung"}'),
    'tempo_trend_before': fields.Nested(taxonomy_item_put, description='{"taxonomy": "TempoEntwicklung"}'),
    'tempo_trend_after': fields.Nested(taxonomy_item_put, description='{"taxonomy": "TempoEntwicklung"}'),
})

tempo_context_get = api.model('TempoContextGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'tempo_context_before': fields.Nested(taxonomy_item_get, description='{"taxonomy": "TempoEinbettung"}'),
    'tempo_context_after': fields.Nested(taxonomy_item_get, description='{"taxonomy": "TempoEinbettung"}'),
    'tempo_trend_before': fields.Nested(taxonomy_item_get, description='{"taxonomy": "TempoEntwicklung"}'),
    'tempo_trend_after': fields.Nested(taxonomy_item_get, description='{"taxonomy": "TempoEntwicklung"}'),
})

form_put = api.model('FormPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'contains_theme': fields.Boolean(default=True),
    'form_schema': fields.Nested(taxonomy_item_put, description='{"taxonomy": "Formschema"}'),
    'formal_function': fields.Nested(taxonomy_item_put, description='{"taxonomy": "FormaleFunktion"}'),
})

form_get = api.model('FormGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'contains_theme': fields.Boolean(default=True),
    'form_schema': fields.Nested(taxonomy_item_get, description='{"taxonomy": "Formschema"}'),
    'formal_function': fields.Nested(taxonomy_item_get, description='{"taxonomy": "FormaleFunktion"}'),
})

harmonic_center_put = api.model('HarmonicCenterPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'tonalitaet': fields.Nested(taxonomy_item_put, description='{"taxonomy": "Tonalitaet"}'),
    'harmonische_funktion': fields.Nested(taxonomy_item_put, description='{"taxonomy": "HarmonischeFunktion"}'),
    'grundton': fields.Nested(taxonomy_item_put, description='{"taxonomy": "Grundton"}'),
    'harmonische_stufe': fields.Nested(taxonomy_item_put, description='{"taxonomy": "HarmonischeStufe"}'),
})

harmonic_center_get = api.model('HarmonicCenterGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'tonalitaet': fields.Nested(taxonomy_item_get, description='{"taxonomy": "Tonalitaet"}'),
    'harmonische_funktion': fields.Nested(taxonomy_item_get, description='{"taxonomy": "HarmonischeFunktion"}'),
    'grundton': fields.Nested(taxonomy_item_get, description='{"taxonomy": "Grundton"}'),
    'harmonische_stufe': fields.Nested(taxonomy_item_get, description='{"taxonomy": "HarmonischeStufe"}'),
})

harmonics_put = api.model('HarmonicsPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'degree_of_dissonance': fields.Nested(taxonomy_item_put, description='{"taxonomy": "Dissonanzgrad"}'),
    'dissonances': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "Dissonanzen", "isArray": true}', default=[]),
    'harmonic_complexity': fields.Nested(taxonomy_item_put, description='{"taxonomy": "HarmonischeKomplexitaet"}'),
    'nr_of_different_chords_per_measure': fields.Float(),
    'harmonic_density': fields.Nested(taxonomy_item_put, description='{"taxonomy": "HarmonischeDichte"}'),
    'nr_of_melody_tones_per_harmony': fields.Float(),
    'melody_tones_in_melody_one': fields.Nested(taxonomy_item_put, description='{"taxonomy": "AnzahlMelodietoene"}'),
    'melody_tones_in_melody_two': fields.Nested(taxonomy_item_put, description='{"taxonomy": "AnzahlMelodietoene"}'),
    'harmonic_rhythm_is_static': fields.Boolean(default=False),
    'harmonic_rhythm_follows_rule': fields.Boolean(default=False),
    'harmonic_phenomenons': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "HarmonischePhaenomene", "isArray": true}', default=[]),
    'harmonic_changes': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "HarmonischeEntwicklung", "isArray": true}', default=[]),
    'harmonische_funktion': fields.Nested(taxonomy_item_put, description='{"taxonomy": "HarmonischeFunktionVerwandschaft"}'),
    'harmonic_centers': fields.List(fields.Nested(harmonic_center_put, description='HarmonicCenter'), default=[]),
})

harmonics_get = api.model('HarmonicsGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'degree_of_dissonance': fields.Nested(taxonomy_item_get, description='{"taxonomy": "Dissonanzgrad"}'),
    'dissonances': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "Dissonanzen", "isArray": true}', default=[]),
    'harmonic_complexity': fields.Nested(taxonomy_item_get, description='{"taxonomy": "HarmonischeKomplexitaet"}'),
    'nr_of_different_chords_per_measure': fields.Float(),
    'harmonic_density': fields.Nested(taxonomy_item_get, description='{"taxonomy": "HarmonischeDichte"}'),
    'nr_of_melody_tones_per_harmony': fields.Float(),
    'melody_tones_in_melody_one': fields.Nested(taxonomy_item_get, description='{"taxonomy": "AnzahlMelodietoene"}'),
    'melody_tones_in_melody_two': fields.Nested(taxonomy_item_get, description='{"taxonomy": "AnzahlMelodietoene"}'),
    'harmonic_phenomenons': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "HarmonischePhaenomene", "isArray": true}', default=[]),
    'harmonic_changes': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "HarmonischeEntwicklung", "isArray": true}', default=[]),
    'harmonische_funktion': fields.Nested(taxonomy_item_get, description='{"taxonomy": "HarmonischeFunktionVerwandschaft"}'),
    'harmonic_centers': fields.List(fields.Nested(harmonic_center_get, description='HarmonicCenter'), default=[]),
})

dramaturgic_context_put = api.model('DramaturgicContextPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'ambitus_context_after': fields.Nested(taxonomy_item_put, description='{"taxonomy": "AmbitusEinbettung"}'),
    'melodic_line_before': fields.Nested(taxonomy_item_put, description='{"taxonomy": "Melodiebewegung"}'),
    'ambitus_change_after': fields.Nested(taxonomy_item_put, description='{"taxonomy": "AmbitusEntwicklung"}'),
    'ambitus_context_before': fields.Nested(taxonomy_item_put, description='{"taxonomy": "AmbitusEinbettung"}'),
    'ambitus_change_before': fields.Nested(taxonomy_item_put, description='{"taxonomy": "AmbitusEntwicklung"}'),
    'melodic_line_after': fields.Nested(taxonomy_item_put, description='{"taxonomy": "Melodiebewegung"}'),
})

dramaturgic_context_get = api.model('DramaturgicContextGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'ambitus_context_after': fields.Nested(taxonomy_item_get, description='{"taxonomy": "AmbitusEinbettung"}'),
    'melodic_line_before': fields.Nested(taxonomy_item_get, description='{"taxonomy": "Melodiebewegung"}'),
    'ambitus_change_after': fields.Nested(taxonomy_item_get, description='{"taxonomy": "AmbitusEntwicklung"}'),
    'ambitus_context_before': fields.Nested(taxonomy_item_get, description='{"taxonomy": "AmbitusEinbettung"}'),
    'ambitus_change_before': fields.Nested(taxonomy_item_get, description='{"taxonomy": "AmbitusEntwicklung"}'),
    'melodic_line_after': fields.Nested(taxonomy_item_get, description='{"taxonomy": "Melodiebewegung"}'),
})

rhythm_put = api.model('RhythmPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'measure_times': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "Taktart", "isArray": true}', default=[]),
    'rhythmic_phenomenons': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "RhythmischesPhaenomen", "isArray": true}', default=[]),
    'rhythm_types': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "Rhythmustyp", "isArray": true}', default=[]),
    'polymetric': fields.Boolean(default=False),
})

rhythm_get = api.model('RhythmGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'measure_times': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "Taktart", "isArray": true}', default=[]),
    'rhythmic_phenomenons': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "RhythmischesPhaenomen", "isArray": true}', default=[]),
    'rhythm_types': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "Rhythmustyp", "isArray": true}', default=[]),
    'polymetric': fields.Boolean(default=False),
})

dynamic_marking_put = api.model('DynamicMarkingPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'lautstaerke_zusatz': fields.Nested(taxonomy_item_put, description='{"taxonomy": "LautstaerkeZusatz"}'),
    'lautstaerke': fields.Nested(taxonomy_item_put, description='{"taxonomy": "Lautstaerke"}'),
})

dynamic_marking_get = api.model('DynamicMarkingGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'lautstaerke_zusatz': fields.Nested(taxonomy_item_get, description='{"taxonomy": "LautstaerkeZusatz"}'),
    'lautstaerke': fields.Nested(taxonomy_item_get, description='{"taxonomy": "Lautstaerke"}'),
})

dynamic_put = api.model('DynamicPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'dynamic_changes': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "LautstaerkeEntwicklung", "isArray": true}', default=[]),
    'dynamic_markings': fields.List(fields.Nested(dynamic_marking_put, description='DynamicMarking'), default=[]),
})

dynamic_get = api.model('DynamicGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'dynamic_changes': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "LautstaerkeEntwicklung", "isArray": true}', default=[]),
    'dynamic_markings': fields.List(fields.Nested(dynamic_marking_get, description='DynamicMarking'), default=[]),
})

satz_put = api.model('SatzPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'satzart_allgemein': fields.Nested(taxonomy_item_put, description='{"taxonomy": "SatzartAllgemein"}'),
    'satzart_speziell': fields.Nested(taxonomy_item_put, description='{"taxonomy": "SatzartSpeziell"}'),
})

satz_get = api.model('SatzGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'satzart_allgemein': fields.Nested(taxonomy_item_get, description='{"taxonomy": "SatzartAllgemein"}'),
    'satzart_speziell': fields.Nested(taxonomy_item_get, description='{"taxonomy": "SatzartSpeziell"}'),
})

musicial_sequence_put = api.model('MusicialSequencePUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'beats': fields.Integer(default=1),
    'flow': fields.Nested(taxonomy_item_put, description='{"taxonomy": "BewegungImTonraum"}'),
    'tonal_corrected': fields.Boolean(default=False),
    'starting_interval': fields.Nested(taxonomy_item_put, description='{"taxonomy": "Intervall"}'),
})

musicial_sequence_get = api.model('MusicialSequenceGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'beats': fields.Integer(default=1),
    'flow': fields.Nested(taxonomy_item_get, description='{"taxonomy": "BewegungImTonraum"}'),
    'tonal_corrected': fields.Boolean(default=False),
    'starting_interval': fields.Nested(taxonomy_item_get, description='{"taxonomy": "Intervall"}'),
})

composition_put = api.model('CompositionPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'sequences': fields.List(fields.Nested(musicial_sequence_put, description='MusicialSequence{"isNested": true, "isArray": true}'), default=[]),
    'nr_varied_repetitions': fields.Integer(default=1),
    'nr_exact_repetitions': fields.Integer(default=1),
})

composition_get = api.model('CompositionGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'sequences': fields.List(fields.Nested(musicial_sequence_get, description='MusicialSequence'), default=[]),
    'nr_varied_repetitions': fields.Integer(default=1),
    'nr_exact_repetitions': fields.Integer(default=1),
})

opus_citation_put = api.model('OpusCitationPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'opus': fields.Nested(opus_get_citation, description='Opus{"reference": "opus"}'),
    'citation_type': fields.Nested(taxonomy_item_put, description='{"taxonomy": "Zitat"}'),
})

opus_citation_get = api.model('OpusCitationGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'opus': fields.Nested(opus_get_citation, description='Opus{"reference": "opus"}'),
    'citation_type': fields.Nested(taxonomy_item_get, description='{"taxonomy": "Zitat"}'),
})

other_citation = api.model('OtherCitation', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'citation': fields.String(default=''),
})

citations_put = api.model('CitationsGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'is_foreign': fields.Boolean(default=False),
    'opus_citations': fields.List(fields.Nested(opus_citation_put, description='{"isNested": true, "isArray": true}'), default=[]),
    'other_citations': fields.List(fields.Nested(other_citation), default=[]),
    'gattung_citations': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "Gattung", "isArray": true}', default=[]),
    'instrument_citations': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "Instrument", "isArray": true}', default=[]),
    'program_citations': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "Programmgegenstand", "isArray": true}', default=[]),
    'tonmalerei_citations': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "Tonmalerei", "isArray": true}', default=[]),
    'composer_citations': fields.List(fields.Nested(person_get), description='{"reference": "person", "isArray": true}', default=[]),
    'epoch_citations': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "Epoche", "isArray": true}', default=[]),
})

citations_get = api.model('CitationsGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'is_foreign': fields.Boolean(default=False),
    'opus_citations': fields.List(fields.Nested(opus_citation_get, description='OpusCitation'), default=[]),
    'other_citations': fields.List(fields.Nested(other_citation), default=[]),
    'gattung_citations': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "Gattung", "isArray": true}', default=[]),
    'instrument_citations': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "Instrument", "isArray": true}', default=[]),
    'program_citations': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "Programmgegenstand", "isArray": true}', default=[]),
    'tonmalerei_citations': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "Tonmalerei", "isArray": true}', default=[]),
    'composer_citations': fields.List(fields.Nested(taxonomy_item_get), description='{"reference": "person", "isArray": true}', default=[]),
    'epoch_citations': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "Epoche", "isArray": true}', default=[]),
})

tempo_put = api.model('TempoPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'tempo_markings': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "Tempo", "isArray": true}', default=[]),
    'tempo_changes': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "TempoEntwicklung", "isArray": true}', default=[]),
    'tempo_context': fields.Nested(tempo_context_put, description='TempoContext{"isNested": true}'),
})

tempo_get = api.model('TempoGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'tempo_markings': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "Tempo", "isArray": true}', default=[]),
    'tempo_changes': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "TempoEntwicklung", "isArray": true}', default=[]),
    'tempo_context': fields.Nested(tempo_context_get, description='TempoContext{"isNested": true}'),
})

rendition_put = api.model('RenditionGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'mood_markings': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "Ausdruck", "isArray": true}', default=[]),
    'technic_markings': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "Spielanweisung", "isArray": true}', default=[]),
    'articulation_markings': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "Artikulation", "isArray": true}', default=[]),
})

rendition_get = api.model('RenditionGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'mood_markings': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "Ausdruck", "isArray": true}', default=[]),
    'technic_markings': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "Spielanweisung", "isArray": true}', default=[]),
    'articulation_markings': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "Artikulation", "isArray": true}', default=[]),
})



measure_model = api.model('Measure', {
    'measure': fields.Integer(default=1, min=1, required=True),
    'from_page': fields.Integer(default=-1, min=-1, required=False),
})

part_links = api.inherit('PartLinks', with_curies, {
    'self': HaLUrl(UrlData('api.part_part_resource', absolute=True,
                           url_data={'id': 'id'}), rquired=False),
    'subpart': HaLUrl(UrlData('api.part_part_subparts_resource', absolute=True,
                              url_data={'id': 'id'}), rquired=False),
})

part_post = api.model('PartPOST', {
    'name': fields.String(required=True, max_length=255, title='Name'),
    'movement': fields.Integer(required=True, min=1, default=1, example=1, title='In Satz'),
    'measure_start': fields.Nested(measure_model, required=True, description='{"isNested": true}', title='Starttakt'),
    'measure_end': fields.Nested(measure_model, required=True, description='{"isNested": true}', title='Endtakt'),
    'length': fields.Integer(default=1, min=1, required=True, example=1, title='Länge'),
})

part_put = api.inherit('PartPUT', part_post, {
    'occurence_in_movement': fields.Nested(taxonomy_item_put, required=True, description='{"taxonomy": "AuftretenSatz"}', title='Vorkommen im Werk'),
    'instrumentation_context': fields.Nested(instrumentation_context_put, required=True, description='{"isNested": true}', title='Kontext der Instrumentierung'),
    'dynamic_context': fields.Nested(dynamic_context_put, required=True, description='{"isNested": true}', title='Kontext der Dynamik'),
    'tempo_context': fields.Nested(tempo_context_put, required=True, description='{"isNested": true}', title='Kontext des Tempos'),
    'dramaturgic_context': fields.Nested(dramaturgic_context_put, required=True, description='{"isNested": true}', title='Kontext der Dramaturgie'),
    'form': fields.Nested(form_put, required=True, description='{"isNested": true}', title='Form'),
})

subpart_links = api.inherit('SubPartLinks', with_curies, {
    'self': HaLUrl(UrlData('api.subpart_sub_part_resource', absolute=True,
                           url_data={'part_id': 'part_id', 'subpart_id':'id'}), rquired=False),
    'voice': HaLUrl(UrlData('api.subpart_sub_part_voice_list_resource', absolute=True,
                            url_data={'subpart_id':'id'}), rquired=False),
})

subpart_post = api.model('SubPartPOST', {
    'label': fields.String(pattern='^[A-Z]\'{0,4}$', required=True, max_length=5, example='A', default='A', title="Label"),
})

subpart_put = api.inherit('SubPartPUT', subpart_post, {
    'label': fields.String(required=True, default='A', title='Label'),
    'occurence_in_part': fields.Nested(taxonomy_item_put, required=True, description='{"taxonomy": "AuftretenWerkausschnitt"}', title='Vorkommen im Werkausschnitt'),
    'share_of_part': fields.Nested(taxonomy_item_put, required=True, description='{"taxonomy": "Anteil"}', title='Anteil am Werkausschnitt'),
    'instrumentation': fields.List(fields.Nested(taxonomy_item_put, required=True), description='{"taxonomy": "Instrument", "isArray": true}', default=[], title='Instrumentierung'),
    'composition': fields.Nested(composition_put, required=True, description='Composition{"isNested": true}', title='Verarbeitung'),
    'rhythm': fields.Nested(rhythm_put, required=True, description='Rhythm{"isNested": true}', title='Rhythmik'),
    'satz': fields.Nested(satz_put, required=True, description='Satz{"isNested": true}', title='Satz'),
    'harmonics': fields.Nested(harmonics_put, required=True, description='Harmonics{"isNested": true}', title='Harmonik'),
    'form': fields.Nested(form_put, required=True, description='Form{"isNested": true}', title='Form'),
    'dynamic': fields.Nested(dynamic_put, required=True, description='Dynamic{"isNested": true}', title='Dynamik'),
    'tempo': fields.Nested(tempo_put, description='TempoGroup{"isNested": true}', title='Tempo'),
    'rendition': fields.Nested(rendition_put, description='Rendition{"isNested": true}', title='Vortrag'),
    'citations': fields.Nested(citations_put, description='Citations{"isNested": true}', title='Beziehungen/Zitate'),
    'musicial_figures': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "MusikalischeWendung", "isArray": true}', default=[], title='Musikalische Wendungen'),
})

voice_links = api.inherit('VoiceLinks', with_curies, {
    'self': HaLUrl(UrlData('api.subpart_sub_part_voice_resource', absolute=True,
                              url_data={'subpart_id':'subpart_id', 'voice_id':'id'}), rquired=False),
    'subpart': HaLUrl(UrlData('api.subpart_sub_part_resource', absolute=True,
                              url_data={'subpart_id':'subpart_id'}), rquired=False),
})

voice_post = api.model('VoicePOST', {
    'name': fields.String(default='', required=True, max_length=255),
})

voice_put = api.inherit('VoicePUT', voice_post, {
    'has_melody': fields.Boolean(default=False),
    'is_symmetric': fields.Boolean(default=False),
    'is_repetitive': fields.Boolean(default=False),
    'cites_own_melody_later': fields.Boolean(default=False),
    'contains_repetition_from_outside': fields.Boolean(default=False),
    'name': fields.String(default='', ),
    'share': fields.Nested(taxonomy_item_put, description='{"taxonomy": "Anteil"}'),
    'occurence_in_part': fields.Nested(taxonomy_item_put, description='{"taxonomy": "AuftretenWerkausschnitt"}'),
    'satz': fields.Nested(satz_put, description='Satz'),
    'highest_pitch': fields.Nested(taxonomy_item_put, description='{"taxonomy": "Grundton"}'),
    'lowest_pitch': fields.Nested(taxonomy_item_put, description='{"taxonomy": "Grundton"}'),
    'highest_octave': fields.Nested(taxonomy_item_put, description='{"taxonomy": "Oktave"}'),
    'lowest_octave': fields.Nested(taxonomy_item_put, description='{"taxonomy": "Oktave"}'),
    'ornaments': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "Verzierung", "isArray": true}', default=[]),
    'melody_form': fields.Nested(taxonomy_item_put, description='{"taxonomy": "Melodieform"}'),
    'intervallik': fields.Nested(taxonomy_item_put, description='{"taxonomy": "Intervallik"}'),
    'dominant_note_values': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "Notenwert", "isArray": true}', default=[]),
    'instrumentation': fields.List(fields.Nested(taxonomy_item_put), description='{"taxonomy": "Instrument", "isArray": true}', default=[]),
})

voice_get = api.inherit('VoiceGET', voice_post, {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'subpart_id': fields.Integer(default=1, readonly=True, example=1),
    '_links': NestedFields(voice_links),
    'name': fields.String(default='', ),
    'has_melody': fields.Boolean(default=False),
    'is_symmetric': fields.Boolean(default=False),
    'is_repetitive': fields.Boolean(default=False),
    'cites_own_melody_later': fields.Boolean(default=False),
    'contains_repetition_from_outside': fields.Boolean(default=False),
    'share': fields.Nested(taxonomy_item_get, description='{"taxonomy": "Anteil"}'),
    'occurence_in_part': fields.Nested(taxonomy_item_get, description='{"taxonomy": "AuftretenWerkausschnitt"}'),
    'satz': fields.Nested(satz_get, description='Satz'),
    'highest_pitch': fields.Nested(taxonomy_item_get, description='{"taxonomy": "Grundton"}'),
    'lowest_pitch': fields.Nested(taxonomy_item_get, description='{"taxonomy": "Grundton"}'),
    'highest_octave': fields.Nested(taxonomy_item_get, description='{"taxonomy": "Oktave"}'),
    'lowest_octave': fields.Nested(taxonomy_item_get, description='{"taxonomy": "Oktave"}'),
    'ornaments': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "Verzierung", "isArray": true}', default=[]),
    'melody_form': fields.Nested(taxonomy_item_get, description='{"taxonomy": "Melodieform"}'),
    'intervallik': fields.Nested(taxonomy_item_get, description='{"taxonomy": "Intervallik"}'),
    'dominant_note_values': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "Notenwert", "isArray": true}', default=[]),
    'instrumentation': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "Instrument", "isArray": true}', default=[]),
})

subpart_get = api.inherit('SubPartGET', subpart_put, {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'part_id': fields.Integer(default=1, readonly=True, example=1),
    '_links': NestedFields(subpart_links),
    'occurence_in_part': fields.Nested(taxonomy_item_get, description='{"taxonomy": "AuftretenWerkausschnitt"}'),
    'share_of_part': fields.Nested(taxonomy_item_get, description='{"taxonomy": "Anteil"}'),
    'instrumentation': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "Instrument", "isArray": true}', default=[]),
    'instrumentation_context': fields.Nested(instrumentation_context_get),
    'composition': fields.Nested(composition_get, description='Composition'),
    'rhythm': fields.Nested(rhythm_get, description='Rhythm'),
    'satz': fields.Nested(satz_get, description='Satz'),
    'dynamic_context': fields.Nested(dynamic_context_get, description='DynamicContext'),
    'harmonics': fields.Nested(harmonics_get, description='Harmonics'),
    'form': fields.Nested(form_get, description='Form'),
    'dynamic': fields.Nested(dynamic_get, description='Dynamic'),
    'tempo': fields.Nested(tempo_get, description='TempoGroup'),
    'rendition': fields.Nested(rendition_get, description='Rendition'),
    'citations': fields.Nested(citations_get, description='Citations'),
    'musicial_figures': fields.List(fields.Nested(taxonomy_item_get), description='{"taxonomy": "MusikalischeWendung", "isArray": true}', default=[]),
})

part_get = api.inherit('PartGET', part_put, {
    'id': fields.Integer(default=1, required=False, readonly=True, example=1),
    'opus_id': fields.Integer(default=1, readonly=True, example=1),
    '_links': NestedFields(part_links),
    'occurence_in_movement': fields.Nested(taxonomy_item_get),
    'instrumentation_context': fields.Nested(instrumentation_context_get),
    'dynamic_context': fields.Nested(dynamic_context_get),
    'tempo_context': fields.Nested(tempo_context_get),
    'dramaturgic_context': fields.Nested(dramaturgic_context_get, description='DramaturgicContext'),
    'form': fields.Nested(form_get),
    'subparts': fields.List(fields.Nested(subpart_get), default=[]),
})

opus_put = api.inherit('OpusPUT', opus_post, {
    'original_name': fields.String(max_length=255, default='', required=True, title='Name (orig)'),
    'composition_year': fields.Integer(default=-1, required=True, title='Kompositionsjahr'),
    'composition_place': fields.String(max_length=255, default='', required=True, title='Kompositionsort'),
    'notes': fields.String(default='', required=True, title='Notizen'),
    'score_link': fields.String(default='', required=True, description='A url linking to the sheet music.', title='Partitur'),
    'first_printed_at': fields.String(max_length=255, default='', required=True, title='Ort der Partitur'),
    'first_printed_in': fields.Integer(default=-1, required=True, title='Jahr der Partitur'),
    'first_played_at': fields.String(max_length=255, default='', required=True, title='Ort der Uraufführung'),
    'first_played_in': fields.Integer(default=-1, required=True, title='Jahr der Uraufführung'),
    'movements': fields.Integer(default=1, required=True, title='Anzahl Sätze'),
    'genre': fields.Nested(taxonomy_item_put, description='{"taxonomy": "GattungNineteenthCentury"}', required=True, title='Genre'),
    'grundton': fields.Nested(taxonomy_item_put, description='{"taxonomy": "Grundton"}', required=True, title='Grundton'),
    'tonalitaet': fields.Nested(taxonomy_item_put, description='{"taxonomy": "Tonalitaet"}', required=True, title='Tonalität'),
})

opus_get = api.inherit('OpusGET', opus_put, {
    'id': fields.Integer(default=1, readonly=True, example=1),
    '_links': NestedFields(opus_links),
    'composer': fields.Nested(person_get),
    'parts': fields.List(fields.Nested(part_get), default=[]),
    'genre': fields.Nested(taxonomy_item_get),
    'grundton': fields.Nested(taxonomy_item_get),
    'tonalitaet': fields.Nested(taxonomy_item_get),
})
