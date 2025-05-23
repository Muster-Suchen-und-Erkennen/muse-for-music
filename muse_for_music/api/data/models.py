"""Models for data objects."""

from collections import OrderedDict

from flask_restx import fields
from ...hal_field import HaLUrl, NestedFields, EmbeddedFields, NestedModel, UrlData
from . import api
from ..models import with_curies
from ..taxonomies.models import taxonomy_item_get, taxonomy_item_ref
from ...models.data.people import Person
from ...models.data.opus import Opus
from ...models.data.part import Part
from ...models.data.subpart import SubPart
from ...models.data.voice import Voice

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


class EnumField(fields.Raw, fields.StringMixin):
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

person_links = api.model('PersonLinks', OrderedDict([
    ('self', HaLUrl(UrlData('api.person_person_resource', absolute=True, url_data={'id': 'id'}),
                    required=False)),
    ('find', HaLUrl(UrlData('api.person_person_list_resource', absolute=True, templated=True,
                            path_variables=['id']), required=False)),
]))

person_post = api.model('PersonPOST', OrderedDict([
    ('name', fields.String(title='Name', description='Name der Person', min_length=1, max_length=191, default='', required=True, example='admin')),
    ('gender', EnumField(title='Geschlecht', description='Geschlecht der Person', required=True, example='male', enum=['male', 'female', 'other'], enumTranslation={
        'male': 'männlich',
        'female': 'weiblich',
        'other': 'etwas anderes',
    })),
]))

person_put = api.inherit('PersonPUT', person_post, OrderedDict([
    ('birth_date', fields.Integer(title='Geburtsjahr', example=1921, default=-1, nullable=True)),
    ('death_date', fields.Integer(title='Todesjahr', example=1921, default=-1, nullable=True)),
    ('nationality', fields.String(title='Nationalität', max_length=100, default='', nullable=True)),
]))

person_get = api.inherit('PersonGET', person_put, OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('_links', NestedFields(person_links)),
]))



opus_links = api.inherit('OpusLinks', with_curies, OrderedDict([
    ('self', HaLUrl(UrlData('api.opus_opus_resource', absolute=True, url_data={'id': 'id'}),
                    required=False)),
    ('find', HaLUrl(UrlData('api.opus_opus_list_resource', absolute=True,
                            templated=True, path_variables=['id']), required=False)),
    ('person', HaLUrl(UrlData('api.person_person_resource', absolute=True,
                              url_data={'id': 'composer.id'}), required=False)),
    ('part', HaLUrl(UrlData('api.opus_opus_parts_resource', absolute=True,
                            url_data={'id': 'id'}), required=False)),
]))

opus_post = api.model('OpusPOST', OrderedDict([
    ('name', fields.String(min_length=1, max_length=191, default='', required=True, example='duett in g moll', title='Titel')),
    ('composer', fields.Nested(person_get, description='The composer.', reference='person', title='Komponist', required=True)),
]))

opus_get_citation = api.inherit('OpusGETCitation', opus_post, OrderedDict([
    ('id', fields.Integer(default=-1, readonly=True, example=1)),
    ('_links', NestedFields(opus_links)),
    ('name', fields.String(title='Name', default='', required=True)),
    ('original_name', fields.String(title='Name / Opus Nr.', default='', required=True)),
    ('score_link', fields.String(title='Partiturausgabe', default='', required=True, description='Ein Link zu einer Partitur.')),
    ('composition_year', fields.Integer(title='Kompositionsjahr', default=1, required=True)),
]))

instrumentation_context_put = api.model('InstrumentationContextPUT', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('instrumentation_quantity_before', fields.Nested(taxonomy_item_ref, taxonomy='InstrumentierungEinbettungQuantitaet', title='Instrumentierungsquantität davor')),
    ('instrumentation_quality_before', fields.Nested(taxonomy_item_ref, taxonomy='InstrumentierungEinbettungQualitaet', title='Instrumentierungsqualität davor')),
    ('instrumentation_quantity_after', fields.Nested(taxonomy_item_ref, taxonomy='InstrumentierungEinbettungQuantitaet', title='Instrumentierungsquantität danach')),
    ('instrumentation_quality_after', fields.Nested(taxonomy_item_ref, taxonomy='InstrumentierungEinbettungQualitaet', title='Instrumentierungsqualität danach')),
]))

instrumentation_context_get = api.model('InstrumentationContextGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('instrumentation_quantity_before', fields.Nested(taxonomy_item_get, taxonomy='InstrumentierungEinbettungQuantitaet', title='Instrumentierungsquantität davor')),
    ('instrumentation_quality_before', fields.Nested(taxonomy_item_get, taxonomy='InstrumentierungEinbettungQualitaet', title='Instrumentierungsqualität davor')),
    ('instrumentation_quantity_after', fields.Nested(taxonomy_item_get, taxonomy='InstrumentierungEinbettungQuantitaet', title='Instrumentierungsquantität danach')),
    ('instrumentation_quality_after', fields.Nested(taxonomy_item_get, taxonomy='InstrumentierungEinbettungQualitaet', title='Instrumentierungsqualität danach')),
]))

dynamic_context_put = api.model('DynamicContextPUT', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('loudness_before', fields.Nested(taxonomy_item_ref, taxonomy='Lautstaerke', title='Lautstärke davor')),
    ('dynamic_trend_before', fields.Nested(taxonomy_item_ref, taxonomy='LautstaerkeEinbettung', title='Lautstärke-Entwicklung davor')),
    ('loudness_after', fields.Nested(taxonomy_item_ref, taxonomy='Lautstaerke', title='Lautstärke danach')),
    ('dynamic_trend_after', fields.Nested(taxonomy_item_ref, taxonomy='LautstaerkeEinbettung', title='Lautstärke-Entwicklung danach')),
]))

dynamic_context_get = api.model('DynamicContextGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('loudness_before', fields.Nested(taxonomy_item_get, taxonomy='Lautstaerke', title='Lautstärke davor')),
    ('dynamic_trend_before', fields.Nested(taxonomy_item_get, taxonomy='LautstaerkeEinbettung', title='Lautstärke Einbettung davor')),
    ('loudness_after', fields.Nested(taxonomy_item_get, taxonomy='Lautstaerke', title='Lautstärke danach')),
    ('dynamic_trend_after', fields.Nested(taxonomy_item_get, taxonomy='LautstaerkeEinbettung', title='Lautstärke Einbettung danach')),
]))

tempo_context_put = api.model('TempoContextPUT', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('tempo_context_before', fields.Nested(taxonomy_item_ref, taxonomy='TempoEinbettung', title='Tempo Einbettung davor')),
    ('tempo_trend_before', fields.Nested(taxonomy_item_ref, taxonomy='TempoEntwicklung', title='Tempo-Entwicklung davor')),
    ('tempo_context_after', fields.Nested(taxonomy_item_ref, taxonomy='TempoEinbettung', title='Tempo Einbettung danach')),
    ('tempo_trend_after', fields.Nested(taxonomy_item_ref, taxonomy='TempoEntwicklung', title='Tempo-Entwicklung danach')),
]))

tempo_context_get = api.model('TempoContextGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('tempo_context_before', fields.Nested(taxonomy_item_get, taxonomy='TempoEinbettung', title='Tempo Einbettung davor')),
    ('tempo_trend_before', fields.Nested(taxonomy_item_get, taxonomy='TempoEntwicklung', title='Tempo-Entwicklung davor')),
    ('tempo_context_after', fields.Nested(taxonomy_item_get, taxonomy='TempoEinbettung', title='Tempo Einbettung danach')),
    ('tempo_trend_after', fields.Nested(taxonomy_item_get, taxonomy='TempoEntwicklung', title='Tempo-Entwicklung danach')),
]))

form_put = api.model('FormPUT', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('contains_theme', fields.Boolean(default=False, title='Enthält Thema')),
    ('form_schema', fields.Nested(taxonomy_item_ref, taxonomy='Formschema', title='Formschema')),
    ('formal_functions', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='FormaleFunktion', title='Formale Funktion')),
]))

form_get = api.model('FormGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('contains_theme', fields.Boolean(default=False, title='Enthält Thema')),
    ('form_schema', fields.Nested(taxonomy_item_get, taxonomy='Formschema', title='Formschema')),
    ('formal_functions', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='FormaleFunktion', title='Formale Funktion')),
]))

harmonic_center_put = api.model('HarmonicCenterPUT', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('tonalitaet', fields.Nested(taxonomy_item_ref, taxonomy='Tonalitaet', title='Tonalität')),
    ('harmonische_funktion', fields.Nested(taxonomy_item_ref, taxonomy='HarmonischeFunktion', title='Harmonische Funktion', description='In Bezug auf die Satztonart')),
    ('grundton', fields.Nested(taxonomy_item_ref, taxonomy='Grundton', title='Grundton')),
    ('harmonische_stufe', fields.Nested(taxonomy_item_ref, taxonomy='HarmonischeStufe', title='Harmonische Stufe', description='In Bezug auf die Satztonart')),
]))

harmonic_center_get = api.model('HarmonicCenterGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('tonalitaet', fields.Nested(taxonomy_item_get, taxonomy='Tonalitaet', title='Tonalität')),
    ('harmonische_funktion', fields.Nested(taxonomy_item_get, taxonomy='HarmonischeFunktion', title='Harmonische Funktion', description='In Bezug auf die Satztonart')),
    ('grundton', fields.Nested(taxonomy_item_get, taxonomy='Grundton', title='Grundton')),
    ('harmonische_stufe', fields.Nested(taxonomy_item_get, taxonomy='HarmonischeStufe', title='Harmonische Stufe', description='In Bezug auf die Satztonart')),
]))

harmonics_put = api.model('HarmonicsPUT', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('degree_of_dissonance', fields.Nested(taxonomy_item_ref, taxonomy='Dissonanzgrad', title='Dissonanzgrad')),
    ('numeric_degree_of_dissonance', fields.Float(min=-1, minimum=0, max=100, title='Dissonanzgrad (numerisch)')),
    # ('dissonances', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Dissonanzen', default=[], title='Dissonanzen', description='Nicht ausfüllen. Kategorie wird gestrichen.')),
    ('chords', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Akkord', default=[], title='Klänge', description='Auf ganz wenige, wirklich auffällige Klänge beschränken.\n\nFolgende Klänge werden hier erfasst:\n- Verm. Drei- und Vierklänge (nicht aber bei einem verkürzten Dominantseptnonakkord!)\n- Überm. Dreiklänge\n- Neapolitaner\n- Übermäßiger Quintsextakkord')),
    ('harmonic_complexity', fields.Nested(taxonomy_item_ref, taxonomy='HarmonischeKomplexitaet', title='Harmonische Komplexität', description='Der vom Tool errechnete Wert wird durch die Anzahl der Takte dividiert und dann den Kategorien zugeordnet.')),
    ('numeric_harmonic_complexity', fields.Float(min=-1, minimum=0, max=100, title='Harmonische Komplexität (numerisch)')),
    ('harmonic_density', fields.Nested(taxonomy_item_ref, taxonomy='HarmonischeDichte', title='Harmonische Dichte')),
    ('numeric_harmonic_density', fields.Float(min=-1, minimum=0, max=100, title='Harmonische Dichte (numerisch)')),
    ('harmonic_phenomenons', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='HarmonischePhaenomene', default=[], title='Harmonische Phänomene')),
    ('harmonic_changes', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='HarmonischeEntwicklung', default=[], title='Harmonische Entwicklung')),
    ('harmonische_funktion', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='HarmonischeFunktionVerwandschaft', title='Zeigt Modulation zu Tonart mit folgender Funktion (bezogen auf Werkausschnitt)')),
    ('harmonic_centers', fields.List(fields.Nested(harmonic_center_put, description='HarmonicCenter'), default=[], title='Harmonische Zentren')),
    ('harmonic_analyse', fields.String(default='', title='Harmonische Analyse', description="Freitextfeld für Anmerkungen zur harmonischen Analyse (z.B. die errechneten Werte des Tools).", nullable=True)),
]))

harmonics_get = api.model('HarmonicsGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('degree_of_dissonance', fields.Nested(taxonomy_item_get, taxonomy='Dissonanzgrad', title='Dissonanzgrad')),
    ('numeric_degree_of_dissonance', fields.Float(min=-1, max=100, title='Dissonanzgrad (numerisch)')),
    # ('dissonances', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Dissonanzen', default=[], title='Dissonanzen')),
    ('harmonic_complexity', fields.Nested(taxonomy_item_get, taxonomy='HarmonischeKomplexitaet', title='Harmonische Komplexität')),
    ('numeric_harmonic_complexity', fields.Float(min=-1, max=100, title='Harmonische Komplexität (numerisch)')),
    ('harmonic_density', fields.Nested(taxonomy_item_get, taxonomy='HarmonischeDichte', title='Harmonische Dichte')),
    ('numeric_harmonic_density', fields.Float(min=-1, max=100, title='Harmonische Dichte (numerisch)')),
    ('harmonic_phenomenons', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='HarmonischePhaenomene', default=[], title='Harmonische Phänomene')),
    ('harmonic_changes', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='HarmonischeEntwicklung', default=[], title='Harmonische Entwicklung')),
    ('harmonische_funktion', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='HarmonischeFunktionVerwandschaft', title='Zeigt Modulation zu Tonart mit folgender Funktion (bezogen auf Werkausschnitt)')),
    ('harmonic_centers', fields.List(fields.Nested(harmonic_center_get, description='HarmonicCenter'), default=[], title='Harmonische Zentren')),
]))

dramaturgic_context_put = api.model('DramaturgicContextPUT', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('ambitus_context_before', fields.Nested(taxonomy_item_ref, taxonomy='AmbitusEinbettung', title='Ambitus Einbettung davor')),
    ('ambitus_change_before', fields.Nested(taxonomy_item_ref, taxonomy='AmbitusEntwicklung', title='Ambitus-Entwicklung davor')),
    ('melodic_line_before', fields.Nested(taxonomy_item_ref, taxonomy='Melodiebewegung', title='Melodielinie davor', description='Bezogen auf die 5-10 vorangehenden Takte.')),
    ('ambitus_context_after', fields.Nested(taxonomy_item_ref, taxonomy='AmbitusEinbettung', title='Ambitus Einbettung danach')),
    ('ambitus_change_after', fields.Nested(taxonomy_item_ref, taxonomy='AmbitusEntwicklung', title='Ambitus-Entwicklung danach')),
    ('melodic_line_after', fields.Nested(taxonomy_item_ref, taxonomy='Melodiebewegung', title='Melodielinie danach', description='Bezogen auf die 5-10 nachfolgenden Takte.')),
]))

dramaturgic_context_get = api.model('DramaturgicContextGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('ambitus_context_before', fields.Nested(taxonomy_item_get, taxonomy='AmbitusEinbettung', title='Ambitus Einbettung davor')),
    ('ambitus_change_before', fields.Nested(taxonomy_item_get, taxonomy='AmbitusEntwicklung', title='Ambitus-Entwicklung davor')),
    ('melodic_line_before', fields.Nested(taxonomy_item_get, taxonomy='Melodiebewegung', title='Melodielinie davor')),
    ('ambitus_context_after', fields.Nested(taxonomy_item_get, taxonomy='AmbitusEinbettung', title='Ambitus Einbettung danach')),
    ('ambitus_change_after', fields.Nested(taxonomy_item_get, taxonomy='AmbitusEntwicklung', title='Ambitus-Entwicklung danach')),
    ('melodic_line_after', fields.Nested(taxonomy_item_get, taxonomy='Melodiebewegung', title='Melodielinie danach')),
]))

rhythm_put = api.model('RhythmPUT', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('measure_times', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Taktart', default=[], title='Taktarten')),
    ('rhythmic_phenomenons', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='RhythmischesPhaenomen', default=[], title='Rhythmische Phänomene')),
    ('rhythm_types', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Rhythmustyp', default=[], title='Rhythmustypen')),
    ('polymetric', fields.Boolean(default=False, title='Polymetrik')),
]))

rhythm_get = api.model('RhythmGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('measure_times', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Taktart', default=[], title='Taktarten')),
    ('rhythmic_phenomenons', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='RhythmischesPhaenomen', default=[], title='Rhythmische Phänomene')),
    ('rhythm_types', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Rhythmustyp', default=[], title='Rhythmustypen')),
    ('polymetric', fields.Boolean(default=False, title='Polymetrik')),
]))

dynamic_marking_put = api.model('DynamicMarkingPUT', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('lautstaerke', fields.Nested(taxonomy_item_ref, taxonomy='Lautstaerke', title='Lautstärke')),
    ('lautstaerke_zusatz', fields.Nested(taxonomy_item_ref, taxonomy='LautstaerkeZusatz', title='Zusatz')),
]))

dynamic_marking_get = api.model('DynamicMarkingGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('lautstaerke', fields.Nested(taxonomy_item_get, taxonomy='Lautstaerke', title='Lautstärke')),
    ('lautstaerke_zusatz', fields.Nested(taxonomy_item_get, taxonomy='LautstaerkeZusatz', title='Zusatz')),
]))

dynamic_put = api.model('DynamicPUT', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('dynamic_markings', fields.List(fields.Nested(dynamic_marking_put, description='DynamicMarking'), default=[], title='Lautstärke')),
    ('dynamic_changes', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='LautstaerkeEntwicklung', default=[], title='Lautstärke-Entwicklung')),
]))

dynamic_get = api.model('DynamicGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('dynamic_markings', fields.List(fields.Nested(dynamic_marking_get, description='DynamicMarking'), default=[], title='Lautstärke')),
    ('dynamic_changes', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='LautstaerkeEntwicklung', default=[], title='LautstärkeEntwicklung')),
]))

satz_put = api.model('SatzPUT', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('satzart_allgemein', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='SatzartAllgemein', title='Satzart allgemein')),
    ('satzart_speziell', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='SatzartSpeziell', title='Satzart speziell')),
]))

satz_get = api.model('SatzGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('satzart_allgemein', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='SatzartAllgemein', title='Satzart allgemein')),
    ('satzart_speziell', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='SatzartSpeziell', title='Satzart speziell')),
]))

specification_aa = api.model('SpecificationAA', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('path', fields.String(required=True, readonly=True)),
    ('share', fields.Nested(taxonomy_item_ref, taxonomy='SpecAnteil', title='Anteil')),
    ('occurence', fields.Nested(taxonomy_item_ref, taxonomy='SpecAuftreten', title='Auftreten')),
]))

specification_aai = api.inherit('SpecificationAAI', specification_aa, OrderedDict([
    ('instrumentation', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='SpecInstrument', default=[], title='Instrumente')),
]))

specification_put = api.inherit('SpecificationPUT', specification_aai, OrderedDict([]))

specification_get = api.model('SpecificationGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('path', fields.String(required=True, readonly=True)),
    ('share', fields.Nested(taxonomy_item_get, taxonomy='SpecAnteil', title='Anteil')),
    ('occurence', fields.Nested(taxonomy_item_get, taxonomy='SpecAuftreten', title='Auftreten')),
    ('instrumentation', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='SpecInstrument', default=[], title='Instrumente')),
]))

specification_provider_put = [
    ('specifications', fields.List(fields.Nested(specification_put, description='Specifications'), isArray=True, default=[])),
]

specification_provider_get = [
    ('specifications', fields.List(fields.Nested(specification_get, description='Specifications'), isArray=True, default=[])),
]

musicial_sequence_put = api.model('MusicialSequencePUT', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('beats', fields.Integer(default=0, title='Zählzeiten')),
    ('flow', fields.Nested(taxonomy_item_ref, taxonomy='BewegungImTonraum', title='Bewegung im Tonraum')),
    ('exact_repetition', fields.Boolean(default=False, title='Exakt wiederholte Intervalle')),
    ('tonal_corrected', fields.Boolean(default=False, title='Tonal angepasst')),
    ('starting_interval', fields.Nested(taxonomy_item_ref, taxonomy='Intervall', title='Intervall der Sequenzierung')),
]))

musicial_sequence_get = api.model('MusicialSequenceGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('beats', fields.Integer(default=0, title='Zählzeiten')),
    ('flow', fields.Nested(taxonomy_item_get, taxonomy='BewegungImTonraum', title='Bewegung im Tonraum')),
    ('exact_repetition', fields.Boolean(default=False, title='Exakt wiederholte Intervalle')),
    ('tonal_corrected', fields.Boolean(default=False, title='Tonal angepasst')),
    ('starting_interval', fields.Nested(taxonomy_item_get, taxonomy='Intervall', title='Intervall der Sequenzierung')),
]))

composition_put = api.model('CompositionPUT', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('nr_repetitions_1_2', fields.Integer(default=0, example=0, title='Anzahl Wiederholungen (2 oder weniger Takte)', description="Mindestens 3 Vorkommen, einschließlich des ersten Vorkommens.")),
    ('nr_repetitions_3_4', fields.Integer(default=0, title='Anzahl Wiederholungen (3-4 Takte)', description="Mindestens 3 Vorkommen, einschließlich des ersten Vorkommens.")),
    ('nr_repetitions_5_6', fields.Integer(default=0, title='Anzahl Wiederholungen (5-6 Takte)', description="Mindestens 3 Vorkommen, einschließlich des ersten Vorkommens.")),
    ('nr_repetitions_7_10', fields.Integer(default=0, title='Anzahl Wiederholungen (7 oder mehr Takte)', description="Mindestens 3 Vorkommen, einschließlich des ersten Vorkommens.")),
    ('composition_techniques', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Verarbeitungstechnik', default=[], title='motivisch-thematische Arbeit')),
    ('sequences', fields.List(fields.Nested(musicial_sequence_put), default=[], title='Musikalische Sequenz')),
]))

composition_get = api.model('CompositionGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('nr_repetitions_1_2', fields.Integer(default=0, title='Anzahl Wiederholungen (1 oder weniger Takte)', description="Mindestens 3 Vorkommen, einschließlich des ersten Vorkommens.")),
    ('nr_repetitions_3_4', fields.Integer(default=0, title='Anzahl Wiederholungen (3-4 Takte)', description="Mindestens 3 Vorkommen, einschließlich des ersten Vorkommens.")),
    ('nr_repetitions_5_6', fields.Integer(default=0, title='Anzahl Wiederholungen (5-6 Takte)', description="Mindestens 3 Vorkommen, einschließlich des ersten Vorkommens.")),
    ('nr_repetitions_7_10', fields.Integer(default=0, title='Anzahl Wiederholungen (7 oder mehr Takte)', description="Mindestens 3 Vorkommen, einschließlich des ersten Vorkommens.")),
    ('composition_techniques', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Verarbeitungstechnik', default=[], title='motivisch-thematische Arbeit')),
    ('sequences', fields.List(fields.Nested(musicial_sequence_get, description='MusicialSequence'), default=[], title='Musikalische Sequenz')),
]))

opus_citation_put = api.model('OpusCitationPUT', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('opus', fields.Nested(opus_get_citation, reference='opus', title='Werk')),
    ('citation_type', fields.Nested(taxonomy_item_ref, taxonomy='Zitat', title='Art des Zitats')),
]))

opus_citation_get = api.model('OpusCitationGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('opus', fields.Nested(opus_get_citation, reference='opus', title='Werk')),
    ('citation_type', fields.Nested(taxonomy_item_get, taxonomy='Zitat', title='Art des Zitats')),
]))

citations_put = api.model('CitationsPUT', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('opus_citations', fields.List(fields.Nested(opus_citation_put), isNested=True, isArray=True, default=[], title='Zitiert folgende Werke')),
    ('gattung_citations', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Gattung', default=[], title='Zitiert folgende Gattungen')),
    ('instrument_citations', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Instrument', default=[], title='Zitiert folgende Instrumente')),
    ('composer_citations', fields.List(fields.Nested(person_get), isArray=True, reference='person', default=[], title='Zitiert Personalstil von')),
    ('program_citations', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Programmgegenstand', default=[], title='Programmgegenstand')),
    ('tonmalerei_citations', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Tonmalerei', default=[], title='Tonmalerei')),
    ('epoch_citations', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Epoche', default=[], title='Zitiert folgende Epochen')),
]))

citations_get = api.model('CitationsGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('opus_citations', fields.List(fields.Nested(opus_citation_get, description='OpusCitation'), default=[], title='Zitiert folgende Werke')),
    ('gattung_citations', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Gattung', default=[], title='Zitiert folgende Gattungen')),
    ('instrument_citations', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Instrument', default=[], title='Zitiert folgende Instrumente')),
    ('composer_citations', fields.List(fields.Nested(person_get), isArray=True, reference='person', default=[], title='Zitiert Personalstil von')),
    ('program_citations', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Programmgegenstand', default=[], title='Programmgegenstand')),
    ('tonmalerei_citations', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Tonmalerei', default=[], title='Tonmalerei')),
    ('epoch_citations', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Epoche', default=[], title='Zitiert folgende Epochen')),
]))

tempo_put = api.model('TempoPUT', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('tempo_markings', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Tempo', default=[], title='Tempo')),
    ('tempo_changes', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='TempoEntwicklung', default=[], title='Tempo-Entwicklung')),
]))

tempo_get = api.model('TempoGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('tempo_markings', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Tempo', default=[], title='Tempo')),
    ('tempo_changes', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='TempoEntwicklung', default=[], title='Tempo-Entwicklung')),
]))

ambitus_put = api.model('AmbitusPUT', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('highest_pitch', fields.Nested(taxonomy_item_ref, taxonomy='Grundton', title='Höchster Ton')),
    ('highest_octave', fields.Nested(taxonomy_item_ref, taxonomy='Oktave', title='Höchste Oktave')),
    ('lowest_pitch', fields.Nested(taxonomy_item_ref, taxonomy='Grundton', title='Niedrigster Ton')),
    ('lowest_octave', fields.Nested(taxonomy_item_ref, taxonomy='Oktave', title='Niedrigste Oktave')),
]))

ambitus_get = api.model('AmbitusGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('highest_pitch', fields.Nested(taxonomy_item_get, taxonomy='Grundton', title='Höchster Ton')),
    ('highest_octave', fields.Nested(taxonomy_item_get, taxonomy='Oktave', title='Höchste Oktave')),
    ('lowest_pitch', fields.Nested(taxonomy_item_get, taxonomy='Grundton', title='Niedrigster Ton')),
    ('lowest_octave', fields.Nested(taxonomy_item_get, taxonomy='Oktave', title='Niedrigste Oktave')),
]))

rendition_put = api.model('RenditionGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('mood_markings', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Ausdruck', default=[], title='Ausdruck')),
    ('technic_markings', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Spielanweisung', default=[], title='Spielanweisungen')),
    ('articulation_markings', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Artikulation', default=[], title='Artikulation')),
]))

rendition_get = api.model('RenditionGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('mood_markings', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Ausdruck', default=[], title='Ausdruck')),
    ('technic_markings', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Spielanweisung', default=[], title='Spielanweisungen')),
    ('articulation_markings', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Artikulation', default=[], title='Artikulation')),
]))


measure_model = api.model('Measure', OrderedDict([
    ('measure', fields.Integer(default=1, min=1, required=True, title='Takt')),
    ('from_page', fields.Integer(default=-1, min=-1, required=False, nullable=True, title='Relativ zu Seite')),
]))

part_links = api.inherit('PartLinks', with_curies, OrderedDict([
    ('self', HaLUrl(UrlData('api.part_part_resource', absolute=True,
                            url_data={'id': 'id'}), rquired=False)),
    ('subpart', HaLUrl(UrlData('api.part_part_subparts_resource', absolute=True,
                               url_data={'id': 'id'}), rquired=False)),
]))

part_post = api.model('PartPOST', OrderedDict([
    ('name', fields.String(required=True, max_length=191, title='Name')),
    ('movement', fields.Integer(required=True, min=1, default=1, example=1, title='In Satz')),
    ('measure_start', fields.Nested(measure_model, required=True, isNested=True, title='Starttakt')),
    ('measure_end', fields.Nested(measure_model, required=True, isNested=True, title='Endtakt')),
    ('length', fields.Integer(default=1, min=1, required=True, example=1, title='Länge')),
    ('omissions', fields.String(default='', title='Ausgelassene Takte', nullable=True)),
]))

part_put = api.inherit('PartPUT', part_post, OrderedDict([
    ('occurence_in_movement', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='AuftretenSatz', title='Vorkommen im Werk')),
    ('instrumentation_context', fields.Nested(instrumentation_context_put, required=True, isNested=True, title='Kontext der Instrumentierung', allowSave=True)),
    ('dynamic_context', fields.Nested(dynamic_context_put, required=True, isNested=True, title='Kontext der Dynamik', allowSave=True)),
    ('tempo_context', fields.Nested(tempo_context_put, required=True, isNested=True, title='Kontext des Tempos', allowSave=True)),
    ('dramaturgic_context', fields.Nested(dramaturgic_context_put, required=True, isNested=True, title='Sonstiger Kontext', allowSave=True)),
    ('formal_functions', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='FormaleFunktion', title='Formale Funktion')),
    *specification_provider_put
]))

subpart_links = api.inherit('SubPartLinks', with_curies, OrderedDict([
    ('self', HaLUrl(UrlData('api.subpart_sub_part_resource', absolute=True,
                            url_data={'part_id': 'part_id', 'subpart_id':'id'}), rquired=False)),
    ('voice', HaLUrl(UrlData('api.subpart_sub_part_voice_list_resource', absolute=True,
                             url_data={'subpart_id':'id'}), rquired=False)),
]))

subpart_post = api.model('SubPartPOST', OrderedDict([
    ('label', fields.String(required=True, max_length=191, example='A', default='A', title="Name")),
    ('measures', fields.String(default='', title='Taktangaben', description="Nur ausfüllen falls abweichend vom Werkausschnitt.", nullable=True)),
]))

subpart_put = api.inherit('SubPartPUT', subpart_post, OrderedDict([
    ('occurence_in_part', fields.Nested(taxonomy_item_ref, required=True, taxonomy='AuftretenWerkausschnitt', title='Vorkommen im Werkausschnitt')),
    ('share_of_part', fields.Nested(taxonomy_item_ref, required=True, taxonomy='Anteil', title='Anteil am Werkausschnitt')),
    ('instrumentation', fields.List(fields.Nested(taxonomy_item_ref, required=True), required=True, isArray=True, taxonomy='Instrument', default=[], title='Instrumentierung')),
    ('is_tutti', fields.Boolean(required=True, default=False, example=False, title='Entspricht "Tutti"', description='In Bezug auf das gesamte Werk! 80% aller auf einer eigenen Notenzeile notierten Instrumente spielen.')),
    ('harmonics', fields.Nested(harmonics_put, required=True, description='Harmonics', isNested=True, title='Harmonik', allowSave=True)),
    ('dynamic', fields.Nested(dynamic_put, required=True, description='Dynamic', isNested=True, title='Dynamik', allowSave=True)),
    ('tempo', fields.Nested(tempo_put, isNested=True, title='Tempo', allowSave=True)),
]))

voice_links = api.inherit('VoiceLinks', with_curies, OrderedDict([
    ('self', HaLUrl(UrlData('api.subpart_sub_part_voice_resource', absolute=True,
                               url_data={'subpart_id':'subpart_id', 'voice_id':'id'}), rquired=False)),
    ('voice', HaLUrl(UrlData('api.subpart_sub_part_voice_list_resource', absolute=True,
                             url_data={'subpart_id':'subpart_id'}), rquired=False)),
    ('subpart', HaLUrl(UrlData('api.subpart_sub_part_resource', absolute=True,
                               url_data={'subpart_id':'subpart_id'}), rquired=False)),
]))

voice_post = api.model('VoicePOST', OrderedDict([
    ('name', fields.String(default='', required=True, min_length=1, max_length=191, title='Name')),
]))


voice_ref = api.inherit('VoiceREF', voice_post, OrderedDict([
    ('_links', NestedFields(voice_links)),
    ('id', fields.Integer(default=-1, readonly=True, example=1)),
    ('subpart_id', fields.Integer(default=-1, readonly=True, example=1)),
]))

related_voice_put = api.model('RelatedVoicePUT', OrderedDict([
    ('id', fields.Integer(default=-1, readonly=True, example=1)),
    ('type_of_relationship', fields.Nested(taxonomy_item_ref, required=True, taxonomy='VoiceToVoiceRelation', title='Operator')),
    ('related_voice', fields.Nested(voice_ref, required=True, reference='voice', title='Stimme')),
]))

related_voice_get = api.model('RelatedVoiceGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('type_of_relationship', fields.Nested(taxonomy_item_ref, required=True, taxonomy='VoiceToVoiceRelation', title='Operator')),
    ('related_voice', fields.Nested(voice_ref, required=True, reference='voice', title='Stimme')),
]))

voice_put = api.inherit('VoicePUT', voice_post, OrderedDict([
    ('instrumentation', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Instrument', default=[], title='Besetzung')),
    ('ambitus', fields.Nested(ambitus_put, isNested=True, title='Ambitus', allowSave=True)),
    ('has_melody', fields.Boolean(default=False, title='Spielt Melodie')),
    ('musicial_function', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='MusikalischeFunktion', default=[], title='Musikalische Funktionen', description='Alles, was zutrifft, auswählen, insbesondere auch redundante Optionen (z.B. "spielt Begleitung" und "spielt folgende Begleitfigur", etc.).')),
    ('share', fields.Nested(taxonomy_item_ref, taxonomy='Anteil', title='Anteil der Stimme', description='In Bezug auf den Teilwerkausschnitt.')),
    ('occurence_in_part', fields.Nested(taxonomy_item_ref, taxonomy='AuftretenWerkausschnitt', title='Auftreten der Stimme')),
    ('satz', fields.Nested(satz_put, description='Satz', isNested=True, title='Satz')),
    ('rhythm', fields.Nested(rhythm_put, required=True, description='Rhythm', isNested=True, title='Rhythmik', allowSave=True)),
    ('dominant_note_values', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Notenwert', default=[], title='Dominante Notenwerte', description='Es sind bis zu drei dominierende Notenwerte anzugeben. Die Dominanz der Notenwerte bezieht sich auf den Anteil der Zählzeiten, auf denen sie stehen. \nBeispiel: ein Takt mit einer halben Note und zwei Viertelnoten. Hier sind beide Notenwerte gleich dominant, obwohl es mehr Viertel- als halbe Noten gibt. Grund dafür ist, dass sowohl Viertel- als auch halbe Noten je zwei Zählzeiten einnehmen.')),
    ('composition', fields.Nested(composition_put, required=True, description='Composition', isNested=True, title='Verarbeitung', allowSave=True)),
    ('musicial_figures', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='MusikalischeWendung', default=[], title='Musikalische Wendungen')),
    ('rendition', fields.Nested(rendition_put, description='Rendition', isNested=True, title='Vortrag', allowSave=True)),
    ('ornaments', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Verzierung', default=[], title='Verzierungen')),
    ('melody_form', fields.Nested(taxonomy_item_ref, taxonomy='Melodieform', title='Melodik')),
    ('intervallik', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='Intervallik', title='Intervallik')),
    ('intervall_vector', fields.String(default='', title='Intervallvektor', description="[Prime, Sekunde, Terz, Quarte, Triton, Quinte, Sexte, Septime, Oktave, >Oktave]", pattern="\[(\s*[0-9]+\s*,)*(\s*[0-9]+\s*)\]", max_length=2048, nullable=True)),
    ('citations', fields.Nested(citations_put, description='Citations', isNested=True, title='Zitate und Allusionen', allowSave=True)),
    ('related_voices', fields.List(fields.Nested(related_voice_put), isArray=True, default=[], title='Beziehungen zu anderen Stimmen')),
    *specification_provider_put
]))

voice_get = api.inherit('VoiceGET', voice_post, OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('subpart_id', fields.Integer(default=1, readonly=True, example=1)),
    ('_links', NestedFields(voice_links)),
    ('name', fields.String(default='', )),
    ('instrumentation', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Instrument', default=[], title='Besetzung')),
    ('ambitus', fields.Nested(ambitus_get, isNested=True, title='Ambitus', allowSave=True)),
    ('has_melody', fields.Boolean(default=False, title='Spielt Melodie')),
    ('musicial_function', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='MusikalischeFunktion', default=[], title='Musikalische Funktionen', description='Alles, was zutrifft, auswählen, insbesondere auch redundante Optionen (z.B. "spielt Begleitung" und "spielt folgende Begleitfigur", etc.).')),
    ('share', fields.Nested(taxonomy_item_get, taxonomy='Anteil')),
    ('occurence_in_part', fields.Nested(taxonomy_item_get, taxonomy='AuftretenWerkausschnitt')),
    ('satz', fields.Nested(satz_get, description='Satz')),
    ('rhythm', fields.Nested(rhythm_get, required=True, description='Rhythm', isNested=True, title='Rhythmik', allowSave=True)),
    ('dominant_note_values', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Notenwert', default=[], title='Dominante Notenwerte', description='Es sind bis zu drei dominierende Notenwerte anzugeben. Die Dominanz der Notenwerte bezieht sich auf den Anteil der Zählzeiten, auf denen sie stehen. \nBeispiel: ein Takt mit einer halben Note und zwei Viertelnoten. Hier sind beide Notenwerte gleich dominant, obwohl es mehr Viertel- als halbe Noten gibt. Grund dafür ist, dass sowohl Viertel- als auch halbe Noten je zwei Zählzeiten einnehmen.')),
    ('composition', fields.Nested(composition_get, required=True, description='Composition', isNested=True, title='Verarbeitung', allowSave=True)),
    ('musicial_figures', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='MusikalischeWendung', default=[], title='Musikalische Wendungen')),
    ('rendition', fields.Nested(rendition_get, description='Rendition', isNested=True, title='Vortrag', allowSave=True)),
    ('ornaments', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Verzierung', default=[])),
    ('melody_form', fields.Nested(taxonomy_item_get, taxonomy='Melodieform')),
    ('intervallik', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Intervallik')),
    ('citations', fields.Nested(citations_get, description='Citations', isNested=True, title='Zitate und Allusionen', allowSave=True)),
    ('related_voices', fields.List(fields.Nested(related_voice_get), isArray=True, default=[], title='Beziehungen zu anderen Stimmen')),
    *specification_provider_get
]))

subpart_get = api.inherit('SubPartGET', subpart_put, OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('part_id', fields.Integer(default=1, readonly=True, example=1)),
    ('_links', NestedFields(subpart_links)),
    ('occurence_in_part', fields.Nested(taxonomy_item_get, taxonomy='AuftretenWerkausschnitt')),
    ('share_of_part', fields.Nested(taxonomy_item_get, taxonomy='Anteil')),
    ('instrumentation', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='Instrument', default=[])),
    ('harmonics', fields.Nested(harmonics_get, description='Harmonics')),
    ('dynamic', fields.Nested(dynamic_get, description='Dynamic')),
    ('tempo', fields.Nested(tempo_get, description='TempoGroup')),
    *specification_provider_get
    #('ambitus', fields.Nested(ambitus_get, isNested=True, title='Ambitus', allowSave=True)),
]))

part_small = api.inherit('PartSmall', part_put, OrderedDict([
    ('id', fields.Integer(default=1, required=False, readonly=True, example=1)),
    ('opus_id', fields.Integer(default=1, readonly=True, example=1)),
    ('_links', NestedFields(part_links)),
    ('occurence_in_movement', fields.List(fields.Nested(taxonomy_item_ref), isArray=True, taxonomy='AuftretenSatz', title='Vorkommen im Werk')),
    ('instrumentation_context', fields.Nested(instrumentation_context_get)),
    ('dynamic_context', fields.Nested(dynamic_context_get)),
    ('tempo_context', fields.Nested(tempo_context_get)),
    ('dramaturgic_context', fields.Nested(dramaturgic_context_get)),
    ('formal_functions', fields.List(fields.Nested(taxonomy_item_get), isArray=True, taxonomy='FormaleFunktion', title='Formale Funktion')),
]))

part_get = api.inherit('PartGET', part_small, OrderedDict([
    ('subparts', fields.List(fields.Nested(subpart_get), default=[])),
    *specification_provider_get
]))

opus_put = api.inherit('OpusPUT', opus_post, OrderedDict([
    ('original_name', fields.String(max_length=191, default='', required=True, title='Opus Nr.')),
    ('movements', fields.Integer(default=1, required=True, title='Anzahl der Sätze')),
    ('genre', fields.Nested(taxonomy_item_ref, taxonomy='GattungNineteenthCentury', required=True, title='Gattung')),
    ('grundton', fields.Nested(taxonomy_item_ref, taxonomy='Grundton', required=True, title='Grundton')),
    ('tonalitaet', fields.Nested(taxonomy_item_ref, taxonomy='Tonalitaet', description='Hier nur ein Tongeschlecht eintragen (in der Regel das der Anfangs- und Schlusstonika).', required=True, title='Tonalität')),
    ('composition_year', fields.Integer(default=-1, required=True, title='Kompositionsjahr', description='Immer das letzte Jahr angeben, keine Zeitspannen!', nullable=True)),
    ('composition_place', fields.String(max_length=191, default='', required=True, title='Kompositionsort', nullable=True)),
    ('notes', fields.String(default='', title='Notizen', nullable=True)),
    ('score_link', fields.String(default='', required=True, description='Ein Link zu einer Partitur.', title='Partiturausgabe', nullable=True)),
    ('first_printed_at', fields.String(max_length=191, default='', required=True, title='Ort der Partitur', nullable=True)),
    ('first_printed_in', fields.Integer(default=-1, required=True, title='Jahr der Partitur', description='Wenn unbekannt "0" eintragen.', nullable=True)),
    ('first_played_at', fields.String(max_length=191, default='', required=True, title='Ort der Uraufführung', nullable=True)),
    ('first_played_in', fields.Integer(default=-1, required=True, title='Jahr der Uraufführung', nullable=True)),
]))

opus_small = api.inherit('OpusSmall', opus_put, OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('_links', NestedFields(opus_links)),
    ('composer', fields.Nested(person_get)),
    ('genre', fields.Nested(taxonomy_item_get)),
    ('grundton', fields.Nested(taxonomy_item_get)),
    ('tonalitaet', fields.Nested(taxonomy_item_get)),
]))

opus_small_get = api.inherit('OpusSmallGET', opus_small, OrderedDict([
    ('parts', fields.List(fields.Nested(part_small), default=[])),
]))

opus_get = api.inherit('OpusGET', opus_small, OrderedDict([
    ('parts', fields.List(fields.Nested(part_get), default=[])),
]))

history_object_get = api.model('HistoryObjectGET', OrderedDict([
    ('type', fields.String(discriminator=True)),

]))

history_person_get = api.inherit('HistoryPersonGET', history_object_get, OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('_links', NestedFields(person_links)),
    ('name', fields.String),
]))

history_opus_get = api.inherit('HistoryOpusGET', history_object_get, OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('_links', NestedFields(opus_links)),
    ('name', fields.String),
]))

history_part_get = api.inherit('HistoryPartGET', history_object_get, OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('_links', NestedFields(part_links)),
    ('name', fields.String),
    ('opus', fields.Nested(history_opus_get)),
]))

history_subpart_get = api.inherit('HistorySubPartGET', history_object_get, OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('_links', NestedFields(subpart_links)),
    ('name', fields.String(attribute='label')),
    ('part', fields.Nested(history_part_get)),
]))

history_voice_get = api.inherit('HistoryVoiceGET', history_object_get, OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('subpart_id', fields.Integer(default=1, readonly=True, example=1)),
    ('_links', NestedFields(voice_links)),
    ('name', fields.String),
    ('subpart', fields.Nested(history_subpart_get)),
]))

history_get = api.model('HistoryGET', OrderedDict([
    ('id', fields.Integer(default=1, readonly=True, example=1)),
    ('time', fields.DateTime(readonly=True)),
    ('username', fields.String(attribute="user.username", readonly=True)),
    ('method', EnumField(enum=['create', 'update', 'delete'], readonly=True)),
    ('type', EnumField(enum=['person', 'opus', 'part', 'subpart', 'voice'], readonly=True)),
    ('full_resource', fields.Polymorph(mapping={
        Person: history_person_get,
        Opus: history_opus_get,
        Part: history_part_get,
        SubPart: history_subpart_get,
        Voice: history_voice_get,
    })),
]))
