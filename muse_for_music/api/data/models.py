"""Models for data objects."""


from flask_restplus import fields
from ...hal_field import HaLUrl, NestedFields, EmbeddedFields, NestedModel, UrlData
from . import api
from ..models import with_curies
from ..taxonomies.models import taxonomy_item_get, taxonomy_item_ref

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
    'name': fields.String(title='Name', description='Name der Person', max_length=191, default='', required=True, example='admin'),
    'gender': GenderField(title='Geschlecht', description='Geschlecht der Person', required=True, example='male', enum=['male', 'female', 'other'])
})

person_put = api.inherit('PersonPUT', person_post, {
    'canonical_name': fields.String(title='Vollständiger Name', max_length=191, default='', example='admin', nullable=True),
    'birth_date': fields.Date(title='Geburtstag', example='1921-2-4', nullable=True),
    'death_date': fields.Date(title='Todestag', example='1921-3-23', nullable=True),
    'nationality': fields.String(title='Nationalität', max_length=100, default='', nullable=True),
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
    'name': fields.String(max_length=191, default='', required=True, example='duett in g moll', title='Name'),
    'composer': fields.Nested(person_get, description='The composer.', reference='person', title='Komponist', required=True),
})

opus_get_citation = api.inherit('OpusGETCitation', opus_post, {
    'id': fields.Integer(default=1, readonly=True, example=1),
    '_links': NestedFields(opus_links),
    'opus_name': fields.String(title='Name', default='', required=True),
    'original_name': fields.String(title='Name / Opus Nr.', default='', required=True),
    'score_link': fields.String(title='Partitur (Link)', default='', required=True, description='Ein Link zu einer Partitur.'),
    'composition_year': fields.Integer(title='Kompositionsjahr', default=1, required=True),
})

instrumentation_context_put = api.model('InstrumentationContextPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'instrumentation_quantity_before': fields.Nested(taxonomy_item_ref, taxonomy='InstrumentierungEinbettungQuantitaet', title='Instrumentierungsquantät davor'),
    'instrumentation_quantity_after': fields.Nested(taxonomy_item_ref, taxonomy='InstrumentierungEinbettungQuantitaet', title='Instrumentierungsquantät danach'),
    'instrumentation_quality_before': fields.Nested(taxonomy_item_ref, taxonomy='InstrumentierungEinbettungQualitaet', title='Instrumentierungsqualität davor'),
    'instrumentation_quality_after': fields.Nested(taxonomy_item_ref, taxonomy='InstrumentierungEinbettungQualitaet', title='Instrumentierungsqualität danach'),
})

instrumentation_context_get = api.model('InstrumentationContextGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'instrumentation_quantity_before': fields.Nested(taxonomy_item_get, taxonomy='InstrumentierungEinbettungQuantitaet', title='Instrumentierungsquantät davor'),
    'instrumentation_quantity_after': fields.Nested(taxonomy_item_get, taxonomy='InstrumentierungEinbettungQuantitaet', title='Instrumentierungsquantät danach'),
    'instrumentation_quality_before': fields.Nested(taxonomy_item_get, taxonomy='InstrumentierungEinbettungQualitaet', title='Instrumentierungsqualität davor'),
    'instrumentation_quality_after': fields.Nested(taxonomy_item_get, taxonomy='InstrumentierungEinbettungQualitaet', title='Instrumentierungsqualität danach'),
})

dynamic_context_put = api.model('DynamicContextPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'loudness_before': fields.Nested(taxonomy_item_ref, taxonomy='Lautstaerke', title='Lautstärke davor'),
    'loudness_after': fields.Nested(taxonomy_item_ref, taxonomy='Lautstaerke', title='Lautstärke danach'),
    'dynamic_trend_before': fields.Nested(taxonomy_item_ref, taxonomy='LautstaerkeEinbettung', title='Lautstärkeentwicklung davor'),
    'dynamic_trend_after': fields.Nested(taxonomy_item_ref, taxonomy='LautstaerkeEinbettung', title='Lautstärkeentwicklung danach'),
})

dynamic_context_get = api.model('DynamicContextGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'loudness_before': fields.Nested(taxonomy_item_get, taxonomy='Lautstaerke', title='Lautstärke davor'),
    'loudness_after': fields.Nested(taxonomy_item_get, taxonomy='Lautstaerke', title='Lautstärke danach'),
    'dynamic_trend_before': fields.Nested(taxonomy_item_get, taxonomy='LautstaerkeEinbettung', title='Lautstärke Einbettung davor'),
    'dynamic_trend_after': fields.Nested(taxonomy_item_get, taxonomy='LautstaerkeEinbettung', title='Lautstärke Einbettung danach'),
})

tempo_context_put = api.model('TempoContextPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'tempo_context_before': fields.Nested(taxonomy_item_ref, taxonomy='TempoEinbettung', title='Tempo Einbettung davor'),
    'tempo_context_after': fields.Nested(taxonomy_item_ref, taxonomy='TempoEinbettung', title='Tempo Einbettung danach'),
    'tempo_trend_before': fields.Nested(taxonomy_item_ref, taxonomy='TempoEntwicklung', title='Tempoentwicklung davor'),
    'tempo_trend_after': fields.Nested(taxonomy_item_ref, taxonomy='TempoEntwicklung', title='Tempoentwicklung danach'),
})

tempo_context_get = api.model('TempoContextGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'tempo_context_before': fields.Nested(taxonomy_item_get, taxonomy='TempoEinbettung', title='Tempo Einbettung davor'),
    'tempo_context_after': fields.Nested(taxonomy_item_get, taxonomy='TempoEinbettung', title='Tempo Einbettung danach'),
    'tempo_trend_before': fields.Nested(taxonomy_item_get, taxonomy='TempoEntwicklung', title='Tempoentwicklung davor'),
    'tempo_trend_after': fields.Nested(taxonomy_item_get, taxonomy='TempoEntwicklung', title='Tempoentwicklung danach'),
})

form_put = api.model('FormPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'contains_theme': fields.Boolean(default=False, title='Enthält Thema'),
    'form_schema': fields.Nested(taxonomy_item_ref, taxonomy='Formschema', title='Formschema'),
    'formal_function': fields.Nested(taxonomy_item_ref, taxonomy='FormaleFunktion', title='Formale Funktion'),
})

form_get = api.model('FormGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'contains_theme': fields.Boolean(default=False, title='Enthält Thema'),
    'form_schema': fields.Nested(taxonomy_item_get, taxonomy='Formschema', title='Formschema'),
    'formal_function': fields.Nested(taxonomy_item_get, taxonomy='FormaleFunktion', title='Formale Funktion'),
})

harmonic_center_put = api.model('HarmonicCenterPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'tonalitaet': fields.Nested(taxonomy_item_ref, taxonomy='Tonalitaet', title='Tonalität'),
    'harmonische_funktion': fields.Nested(taxonomy_item_ref, taxonomy='HarmonischeFunktion', title='Harmonische Funktion'),
    'grundton': fields.Nested(taxonomy_item_ref, taxonomy='Grundton', title='Grundton'),
    'harmonische_stufe': fields.Nested(taxonomy_item_ref, taxonomy='HarmonischeStufe', title='Harmonische Stufe'),
})

harmonic_center_get = api.model('HarmonicCenterGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'tonalitaet': fields.Nested(taxonomy_item_get, taxonomy='Tonalitaet', title='Tonalität'),
    'harmonische_funktion': fields.Nested(taxonomy_item_get, taxonomy='HarmonischeFunktion', title='Harmonische Funktion'),
    'grundton': fields.Nested(taxonomy_item_get, taxonomy='Grundton', title='Grundton'),
    'harmonische_stufe': fields.Nested(taxonomy_item_get, taxonomy='HarmonischeStufe', title='Harmonische Stufe'),
})

harmonics_put = api.model('HarmonicsPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'degree_of_dissonance': fields.Nested(taxonomy_item_ref, taxonomy='Dissonanzgrad', title='Dissonanzgrad'),
    'dissonances': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Dissonanzen', default=[], title='Dissonanzen'),
    'harmonic_complexity': fields.Nested(taxonomy_item_ref, taxonomy='HarmonischeKomplexitaet', title='Harmonische Komplexität'),
    'harmonic_density': fields.Nested(taxonomy_item_ref, taxonomy='HarmonischeDichte', title='Harmonische Dichte'),
    'nr_of_melody_tones_per_harmony': fields.Float(default='-1', title='# Melodietöne in Harmonie'),
    'melody_tones_in_melody_one': fields.Nested(taxonomy_item_ref, taxonomy='AnzahlMelodietoene', title='# Melodietöne in Melodie 1'),
    'melody_tones_in_melody_two': fields.Nested(taxonomy_item_ref, taxonomy='AnzahlMelodietoene', title='# Melodietöne in Melodie 2'),
    'harmonic_rhythm_is_static': fields.Boolean(default=False, title='Statischer Rhythmus'),
    'harmonic_rhythm_follows_rule': fields.Boolean(default=False, title='Rhythmus folgt einer Regel'),
    'harmonic_phenomenons': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='HarmonischePhaenomene', default=[], title='Harmonische Phänomene'),
    'harmonic_changes': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='HarmonischeEntwicklung', default=[], title='Harmonische Entwicklung'),
    'harmonische_funktion': fields.Nested(taxonomy_item_ref, taxonomy='HarmonischeFunktionVerwandschaft', title='Zeigt Modulation zu Tonart mit folgender Funktion (bezogen auf Werkausschnitt)'),
    'harmonic_centers': fields.List(fields.Nested(harmonic_center_put, description='HarmonicCenter'), default=[], title='Harmonische Zentren'),
})

harmonics_get = api.model('HarmonicsGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'degree_of_dissonance': fields.Nested(taxonomy_item_get, taxonomy='Dissonanzgrad', title='Dissonanzgrad'),
    'dissonances': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Dissonanzen', default=[], title='Dissonanzen'),
    'harmonic_complexity': fields.Nested(taxonomy_item_get, taxonomy='HarmonischeKomplexitaet', title='Harmonische Komplexität'),
    'harmonic_density': fields.Nested(taxonomy_item_get, taxonomy='HarmonischeDichte', title='Harmonische Dichte'),
    'nr_of_melody_tones_per_harmony': fields.Float(default='-1', title='# Melodietöne in Harmonie'),
    'melody_tones_in_melody_one': fields.Nested(taxonomy_item_get, taxonomy='AnzahlMelodietoene', title='# Melodietöne in Melodie 1'),
    'melody_tones_in_melody_two': fields.Nested(taxonomy_item_get, taxonomy='AnzahlMelodietoene', title='# Melodietöne in Melodie 2'),
    'harmonic_rhythm_is_static': fields.Boolean(default=False, title='Statischer Harmonischer-Rhythmus'),
    'harmonic_rhythm_follows_rule': fields.Boolean(default=False, title='Harmonischer-Rhythmus folgt einer Regel'),
    'harmonic_phenomenons': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='HarmonischePhaenomene', default=[], title='Harmonische Phänomene'),
    'harmonic_changes': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='HarmonischeEntwicklung', default=[], title='Harmonische Entwicklung'),
    'harmonische_funktion': fields.Nested(taxonomy_item_get, taxonomy='HarmonischeFunktionVerwandschaft', title='Zeigt Modulation zu Tonart mit folgender Funktion (bezogen auf Werkausschnitt)'),
    'harmonic_centers': fields.List(fields.Nested(harmonic_center_get, description='HarmonicCenter'), default=[], title='Harmonische Zentren'),
})

dramaturgic_context_put = api.model('DramaturgicContextPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'ambitus_context_before': fields.Nested(taxonomy_item_ref, taxonomy='AmbitusEinbettung', title='Ambitus Einbettung davor'),
    'ambitus_context_after': fields.Nested(taxonomy_item_ref, taxonomy='AmbitusEinbettung', title='Ambitus Einbettung danach'),
    'ambitus_change_before': fields.Nested(taxonomy_item_ref, taxonomy='AmbitusEntwicklung', title='Ambitusentwicklung davor'),
    'ambitus_change_after': fields.Nested(taxonomy_item_ref, taxonomy='AmbitusEntwicklung', title='Ambitusentwicklung danach'),
    'melodic_line_before': fields.Nested(taxonomy_item_ref, taxonomy='Melodiebewegung', title='Melodielinie davor'),
    'melodic_line_after': fields.Nested(taxonomy_item_ref, taxonomy='Melodiebewegung', title='Melodielinie danach'),
})

dramaturgic_context_get = api.model('DramaturgicContextGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'ambitus_context_before': fields.Nested(taxonomy_item_get, taxonomy='AmbitusEinbettung', title='Ambitus Einbettung davor'),
    'ambitus_context_after': fields.Nested(taxonomy_item_get, taxonomy='AmbitusEinbettung', title='Ambitus Einbettung danach'),
    'ambitus_change_before': fields.Nested(taxonomy_item_get, taxonomy='AmbitusEntwicklung', title='Ambitusentwicklung davor'),
    'ambitus_change_after': fields.Nested(taxonomy_item_get, taxonomy='AmbitusEntwicklung', title='Ambitusentwicklung danach'),
    'melodic_line_before': fields.Nested(taxonomy_item_get, taxonomy='Melodiebewegung', title='Melodielinie davor'),
    'melodic_line_after': fields.Nested(taxonomy_item_get, taxonomy='Melodiebewegung', title='Melodielinie danach'),
})

rhythm_put = api.model('RhythmPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'measure_times': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Taktart', default=[], title='Taktarten'),
    'rhythmic_phenomenons': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='RhythmischesPhaenomen', default=[], title='Rhythmische Phänomene'),
    'rhythm_types': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Rhythmustyp', default=[], title='Rhythmustypen'),
    'polymetric': fields.Boolean(default=False, title='Polymetrik'),
})

rhythm_get = api.model('RhythmGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'measure_times': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Taktart', default=[], title='Taktarten'),
    'rhythmic_phenomenons': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='RhythmischesPhaenomen', default=[], title='Rhythmische Phänomene'),
    'rhythm_types': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Rhythmustyp', default=[], title='Rhythmustypen'),
    'polymetric': fields.Boolean(default=False, title='Polymetrik'),
})

dynamic_marking_put = api.model('DynamicMarkingPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'lautstaerke': fields.Nested(taxonomy_item_ref, taxonomy='Lautstaerke', title='Lautstärke'),
    'lautstaerke_zusatz': fields.Nested(taxonomy_item_ref, taxonomy='LautstaerkeZusatz', title='Zusatz'),
})

dynamic_marking_get = api.model('DynamicMarkingGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'lautstaerke': fields.Nested(taxonomy_item_get, taxonomy='Lautstaerke', title='Lautstärke'),
    'lautstaerke_zusatz': fields.Nested(taxonomy_item_get, taxonomy='LautstaerkeZusatz', title='Zusatz'),
})

dynamic_put = api.model('DynamicPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'dynamic_markings': fields.List(fields.Nested(dynamic_marking_put, description='DynamicMarking'), default=[], title='Dynamik'),
    'dynamic_changes': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='LautstaerkeEntwicklung', default=[], title='Lautstärkeentwicklung'),
})

dynamic_get = api.model('DynamicGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'dynamic_markings': fields.List(fields.Nested(dynamic_marking_get, description='DynamicMarking'), default=[], title='Dynamik'),
    'dynamic_changes': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='LautstaerkeEntwicklung', default=[], title='Lautstärkeentwicklung'),
})

satz_put = api.model('SatzPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'satzart_allgemein': fields.Nested(taxonomy_item_ref, taxonomy='SatzartAllgemein', title='Satzart allgemein'),
    'satzart_speziell': fields.Nested(taxonomy_item_ref, taxonomy='SatzartSpeziell', title='Satzart speziell'),
})

satz_get = api.model('SatzGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'satzart_allgemein': fields.Nested(taxonomy_item_get, taxonomy='SatzartAllgemein', title='Satzart allgemein'),
    'satzart_speziell': fields.Nested(taxonomy_item_get, taxonomy='SatzartSpeziell', title='Satzart speziell'),
})

musicial_sequence_put = api.model('MusicialSequencePUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'beats': fields.Integer(default=1, title='Zählzeiten'),
    'flow': fields.Nested(taxonomy_item_ref, taxonomy='BewegungImTonraum', title='Bewegung im Tonraum'),
    'tonal_corrected': fields.Boolean(default=False, title='Tonal angepasst'),
    'starting_interval': fields.Nested(taxonomy_item_ref, taxonomy='Intervall', title='Startintervall'),
})

musicial_sequence_get = api.model('MusicialSequenceGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'beats': fields.Integer(default=1, title='Zählzeiten'),
    'flow': fields.Nested(taxonomy_item_get, taxonomy='BewegungImTonraum', title='Bewegung im Tonraum'),
    'tonal_corrected': fields.Boolean(default=False, title='Tonal angepasst'),
    'starting_interval': fields.Nested(taxonomy_item_get, taxonomy='Intervall', title='Startintervall'),
})

composition_put = api.model('CompositionPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'nr_repetitions_1_2': fields.Integer(default=0, example=0, title='Anzahl Wiederholungen (1-2 Takte)'),
    'nr_repetitions_3_4': fields.Integer(default=0, title='Anzahl Wiederholungen (3-4 Takte)'),
    'nr_repetitions_5_6': fields.Integer(default=0, title='Anzahl Wiederholungen (5-6 Takte)'),
    'nr_repetitions_7_10': fields.Integer(default=0, title='Anzahl Wiederholungen (7-10 Takte)'),
    'composition_techniques': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Verarbeitungstechnik', default=[], title='Verarbeitungstechnik'),
    'sequences': fields.List(fields.Nested(musicial_sequence_put), default=[], title='Musikalische Sequenz'),
})

composition_get = api.model('CompositionGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'nr_repetitions_1_2': fields.Integer(default=0, title='Anzahl Wiederholungen (1-2 Takte)'),
    'nr_repetitions_3_4': fields.Integer(default=0, title='Anzahl Wiederholungen (3-4 Takte)'),
    'nr_repetitions_5_6': fields.Integer(default=0, title='Anzahl Wiederholungen (5-6 Takte)'),
    'nr_repetitions_7_10': fields.Integer(default=0, title='Anzahl Wiederholungen (7-10 Takte)'),
    'composition_techniques': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Verarbeitungstechnik', default=[], title='Verarbeitungstechnik'),
    'sequences': fields.List(fields.Nested(musicial_sequence_get, description='MusicialSequence'), default=[], title='Musikalische Sequenz'),
})

opus_citation_put = api.model('OpusCitationPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'opus': fields.Nested(opus_get_citation, reference='opus', title='Zitiertes Werk'),
    'citation_type': fields.Nested(taxonomy_item_ref, taxonomy='Zitat', title='Art des Zitats'),
})

opus_citation_get = api.model('OpusCitationGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'opus': fields.Nested(opus_get_citation, reference='opus', title='Zitiertes Werk'),
    'citation_type': fields.Nested(taxonomy_item_get, taxonomy='Zitat', title='Art des Zitats'),
})

other_citation = api.model('OtherCitation', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'citation': fields.String(default='', title='Zitat'),
})

citations_put = api.model('CitationsGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'is_foreign': fields.Boolean(default=False, title='Ist fremd'),
    'opus_citations': fields.List(fields.Nested(opus_citation_put), isNested=True, isArray=True, default=[], title='Zitiert folgende Werke'),
    'other_citations': fields.List(fields.Nested(other_citation), default=[], title='Andere Zitate'),
    'gattung_citations': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Gattung', default=[], title='Zitiert folgende Gattungen'),
    'instrument_citations': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Instrument', default=[], title='Zitiert folgende Instrumente'),
    'program_citations': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Programmgegenstand', default=[], title='Programmgegenstand'),
    'tonmalerei_citations': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Tonmalerei', default=[], title='Tonmalerei'),
    'composer_citations': fields.List(fields.Nested(person_get), isArray=True, reference='person', default=[], title='Zitiert folgenden Komponisten'),
    'epoch_citations': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Epoche', default=[], title='Zitiert folgende Epochen'),
})

citations_get = api.model('CitationsGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'is_foreign': fields.Boolean(default=False, title='Ist fremd'),
    'opus_citations': fields.List(fields.Nested(opus_citation_get, description='OpusCitation'), default=[], title='Zitiert folgende Werke'),
    'other_citations': fields.List(fields.Nested(other_citation), default=[], title='Andere Zitate'),
    'gattung_citations': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Gattung', default=[], title='Zitiert folgende Gattungen'),
    'instrument_citations': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Instrument', default=[], title='Zitiert folgende Instrumente'),
    'program_citations': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Programmgegenstand', default=[], title='Programmgegenstand'),
    'tonmalerei_citations': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Tonmalerei', default=[], title='Tonmalerei'),
    'composer_citations': fields.List(fields.Nested(taxonomy_item_get), isArray=True, reference='person', default=[], title='Zitiert folgenden Komponisten'),
    'epoch_citations': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Epoche', default=[], title='Zitiert folgende Epochen'),
})

tempo_put = api.model('TempoPUT', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'tempo_markings': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Tempo', default=[], title='Tempo'),
    'tempo_changes': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='TempoEntwicklung', default=[], title='Tempoentwicklung'),
    'tempo_context': fields.Nested(tempo_context_put, isNested=True, title='Tempo Einbettung'),
})

tempo_get = api.model('TempoGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'tempo_markings': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Tempo', default=[], title='Tempo'),
    'tempo_changes': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='TempoEntwicklung', default=[], title='Tempoentwicklung'),
    'tempo_context': fields.Nested(tempo_context_get, isNested=True, title='Tempo Einbettung'),
})

rendition_put = api.model('RenditionGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'mood_markings': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Ausdruck', default=[], title='Ausdruck'),
    'technic_markings': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Spielanweisung', default=[], title='Spielanweisungen'),
    'articulation_markings': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Artikulation', default=[], title='Artikulation'),
})

rendition_get = api.model('RenditionGET', {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'mood_markings': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Ausdruck', default=[], title='Ausdruck'),
    'technic_markings': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Spielanweisung', default=[], title='Spielanweisungen'),
    'articulation_markings': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Artikulation', default=[], title='Artikulation'),
})



measure_model = api.model('Measure', {
    'measure': fields.Integer(default=1, min=1, required=True),
    'from_page': fields.Integer(default=-1, min=-1, required=False, nullable=True),
})

part_links = api.inherit('PartLinks', with_curies, {
    'self': HaLUrl(UrlData('api.part_part_resource', absolute=True,
                           url_data={'id': 'id'}), rquired=False),
    'subpart': HaLUrl(UrlData('api.part_part_subparts_resource', absolute=True,
                              url_data={'id': 'id'}), rquired=False),
})

part_post = api.model('PartPOST', {
    'name': fields.String(required=True, max_length=191, title='Name'),
    'movement': fields.Integer(required=True, min=1, default=1, example=1, title='In Satz'),
    'measure_start': fields.Nested(measure_model, required=True, isNested=True, title='Starttakt'),
    'measure_end': fields.Nested(measure_model, required=True, isNested=True, title='Endtakt'),
    'length': fields.Integer(default=1, min=1, required=True, example=1, title='Länge'),
})

part_put = api.inherit('PartPUT', part_post, {
    'occurence_in_movement': fields.Nested(taxonomy_item_ref, required=True, taxonomy='AuftretenSatz', title='Vorkommen im Werk'),
    'instrumentation_context': fields.Nested(instrumentation_context_put, required=True, isNested=True, title='Kontext der Instrumentierung', allowSave=True),
    'dynamic_context': fields.Nested(dynamic_context_put, required=True, isNested=True, title='Kontext der Dynamik', allowSave=True),
    'tempo_context': fields.Nested(tempo_context_put, required=True, isNested=True, title='Kontext des Tempos', allowSave=True),
    'dramaturgic_context': fields.Nested(dramaturgic_context_put, required=True, isNested=True, title='Kontext der Dramaturgie', allowSave=True),
    'form': fields.Nested(form_put, required=True, isNested=True, title='Form', allowSave=True),
})

subpart_links = api.inherit('SubPartLinks', with_curies, {
    'self': HaLUrl(UrlData('api.subpart_sub_part_resource', absolute=True,
                           url_data={'part_id': 'part_id', 'subpart_id':'id'}), rquired=False),
    'voice': HaLUrl(UrlData('api.subpart_sub_part_voice_list_resource', absolute=True,
                            url_data={'subpart_id':'id'}), rquired=False),
})

subpart_post = api.model('SubPartPOST', {
    'label': fields.String(pattern='^[A-Z]\'{0,4}$', required=True, max_length=5, example='A', default='A', title="Label", description='Erlaubte Werte sind "A", "B", …, "Z" sowie "A\'", …, "A\'\'\'\'".'),
})

subpart_put = api.inherit('SubPartPUT', subpart_post, {
    'label': fields.String(required=True, default='A', title='Label'),
    'occurence_in_part': fields.Nested(taxonomy_item_ref, required=True, taxonomy='AuftretenWerkausschnitt', title='Vorkommen im Werkausschnitt'),
    'share_of_part': fields.Nested(taxonomy_item_ref, required=True, taxonomy='Anteil', title='Anteil am Werkausschnitt'),
    'instrumentation': fields.List(fields.Nested(taxonomy_item_ref, required=True), isArray=True, taxonomy='Instrument', default=[], title='Instrumentierung'),
    'composition': fields.Nested(composition_put, required=True, description='Composition', isNested=True, title='Verarbeitung', allowSave=True),
    'rhythm': fields.Nested(rhythm_put, required=True, description='Rhythm', isNested=True, title='Rhythmik', allowSave=True),
    'satz': fields.Nested(satz_put, required=True, description='Satz', isNested=True, title='Satz', allowSave=True),
    'harmonics': fields.Nested(harmonics_put, required=True, description='Harmonics', isNested=True, title='Harmonik', allowSave=True),
    'form': fields.Nested(form_put, required=True, description='Form', isNested=True, title='Form', allowSave=True),
    'dynamic': fields.Nested(dynamic_put, required=True, description='Dynamic', isNested=True, title='Dynamik', allowSave=True),
    'tempo': fields.Nested(tempo_put, description='TempoGroup', isNested=True, title='Tempo', allowSave=True),
    'rendition': fields.Nested(rendition_put, description='Rendition', isNested=True, title='Vortrag', allowSave=True),
    'citations': fields.Nested(citations_put, description='Citations', isNested=True, title='Beziehungen/Zitate', allowSave=True),
    'musicial_figures': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='MusikalischeWendung', default=[], title='Musikalische Wendungen'),
})

voice_links = api.inherit('VoiceLinks', with_curies, {
    'self': HaLUrl(UrlData('api.subpart_sub_part_voice_resource', absolute=True,
                              url_data={'subpart_id':'subpart_id', 'voice_id':'id'}), rquired=False),
    'subpart': HaLUrl(UrlData('api.subpart_sub_part_resource', absolute=True,
                              url_data={'subpart_id':'subpart_id'}), rquired=False),
})

voice_post = api.model('VoicePOST', {
    'name': fields.String(default='', required=True, max_length=191, title='Name'),
})

voice_put = api.inherit('VoicePUT', voice_post, {
    'instrumentation': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Instrument', default=[], title='Besetzung'),
    'has_melody': fields.Boolean(default=False, title='Spielt Melodie'),
    'is_symmetric': fields.Boolean(default=False, title='Ist symmetrisch'),
    'is_repetitive': fields.Boolean(default=False, title='Ist wiederholend'),
    'cites_own_melody_later': fields.Boolean(default=False, title='Enthält selbstzitate'),
    'contains_repetition_from_outside': fields.Boolean(default=False, title='Enthält Wiederholungen von Außerhalb'),
    'share': fields.Nested(taxonomy_item_ref, taxonomy='Anteil', title='Anteil der Stimme'),
    'occurence_in_part': fields.Nested(taxonomy_item_ref, taxonomy='AuftretenWerkausschnitt', title='Auftreten der Stimme'),
    'satz': fields.Nested(satz_put, description='Satz', isNested=True, title='Satz'),
    'highest_pitch': fields.Nested(taxonomy_item_ref, taxonomy='Grundton', title='Höchster Ton'),
    'highest_octave': fields.Nested(taxonomy_item_ref, taxonomy='Oktave', title='Höchste Oktave'),
    'lowest_pitch': fields.Nested(taxonomy_item_ref, taxonomy='Grundton', title='Niedrigster Ton'),
    'lowest_octave': fields.Nested(taxonomy_item_ref, taxonomy='Oktave', title='Niedrigste Oktave'),
    'ornaments': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Verzierung', default=[], title='Verzierungen'),
    'melody_form': fields.Nested(taxonomy_item_ref, taxonomy='Melodieform', title='Melodieform'),
    'intervallik': fields.Nested(taxonomy_item_ref, taxonomy='Intervallik', title='Intervallik'),
    'dominant_note_values': fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Notenwert', default=[], title='Dominante Notenwerte'),
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
    'share': fields.Nested(taxonomy_item_get, taxonomy='Anteil'),
    'occurence_in_part': fields.Nested(taxonomy_item_get, taxonomy='AuftretenWerkausschnitt'),
    'satz': fields.Nested(satz_get, description='Satz'),
    'highest_pitch': fields.Nested(taxonomy_item_get, taxonomy='Grundton'),
    'lowest_pitch': fields.Nested(taxonomy_item_get, taxonomy='Grundton'),
    'highest_octave': fields.Nested(taxonomy_item_get, taxonomy='Oktave'),
    'lowest_octave': fields.Nested(taxonomy_item_get, taxonomy='Oktave'),
    'ornaments': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Verzierung', default=[]),
    'melody_form': fields.Nested(taxonomy_item_get, taxonomy='Melodieform'),
    'intervallik': fields.Nested(taxonomy_item_get, taxonomy='Intervallik'),
    'dominant_note_values': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Notenwert', default=[]),
    'instrumentation': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Instrument', default=[]),
})

subpart_get = api.inherit('SubPartGET', subpart_put, {
    'id': fields.Integer(default=1, readonly=True, example=1),
    'part_id': fields.Integer(default=1, readonly=True, example=1),
    '_links': NestedFields(subpart_links),
    'occurence_in_part': fields.Nested(taxonomy_item_get, taxonomy='AuftretenWerkausschnitt'),
    'share_of_part': fields.Nested(taxonomy_item_get, taxonomy='Anteil'),
    'instrumentation': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Instrument', default=[]),
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
    'musicial_figures': fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='MusikalischeWendung', default=[]),
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
    'original_name': fields.String(max_length=191, default='', required=True, title='Name / Opus Nr.'),
    'movements': fields.Integer(default=1, required=True, title='Anzahl Sätze'),
    'genre': fields.Nested(taxonomy_item_ref, taxonomy='GattungNineteenthCentury', required=True, title='Genre'),
    'grundton': fields.Nested(taxonomy_item_ref, taxonomy='Grundton', required=True, title='Grundton'),
    'tonalitaet': fields.Nested(taxonomy_item_ref, taxonomy='Tonalitaet', required=True, title='Tonalität'),
    'composition_year': fields.Integer(default=-1, required=True, title='Kompositionsjahr', nullable=True),
    'composition_place': fields.String(max_length=191, default='', required=True, title='Kompositionsort', nullable=True),
    'notes': fields.String(default='', required=True, title='Notizen', nullable=True),
    'score_link': fields.String(default='', required=True, description='Ein Link zu einer Partitur.', title='Partitur (Link)', nullable=True),
    'first_printed_at': fields.String(max_length=191, default='', required=True, title='Ort der Partitur', nullable=True),
    'first_printed_in': fields.Integer(default=-1, required=True, title='Jahr der Partitur', nullable=True),
    'first_played_at': fields.String(max_length=191, default='', required=True, title='Ort der Uraufführung', nullable=True),
    'first_played_in': fields.Integer(default=-1, required=True, title='Jahr der Uraufführung', nullable=True),
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
