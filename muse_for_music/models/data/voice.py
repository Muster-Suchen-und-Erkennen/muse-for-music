from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin, UpdateListMixin

from typing import Union, Sequence, Dict

from .measure import Measure
from .subpart import SubPart
from .harmonics import Harmonics
from .satz import Satz
from .dramaturgic_context import DramaturgicContext
from .dynamic import Dynamic, DynamicContext
from .composition import Composition
from .rendition import Rendition
from .rhythm import Rhythm
from .citations import Citations
from .instrumentation import InstrumentationContext, Instrumentation
from ..taxonomies import Anteil, MusikalischeFunktion, Melodieform, Verzierung, \
                         Intervallik, Notenwert, Grundton, Oktave, \
                         AuftretenWerkausschnitt, VoiceToVoiceRelation, \
                         MusikalischeWendung


class Voice(db.Model, GetByID, UpdateableModelMixin, UpdateListMixin):

    _normal_attributes = (
                          ('name', str),
                          ('occurence_in_part', AuftretenWerkausschnitt),
                          ('share', Anteil),
                          ('satz', Satz),
                          ('rhythm', Rhythm),
                          ('composition', Composition),
                          ('rendition', Rendition),
                          ('has_melody', bool),
                          ('melody_form', Melodieform),
                          ('intervallik', Intervallik),
                          ('citations', Citations),
                          )

    _list_attributes = ('dominant_note_values', 'instrumentation', 'ornaments',
                        'musicial_figures', 'musicial_function')

    id = db.Column(db.Integer, primary_key=True)
    subpart_id = db.Column(db.Integer, db.ForeignKey('sub_part.id'), nullable=False)
    name = db.Column(db.String(191), nullable=True)
    instrumentation_id = db.Column(db.Integer, db.ForeignKey('instrumentation.id', ondelete='CASCADE'), nullable=False)
    satz_id = db.Column(db.Integer, db.ForeignKey('satz.id'), nullable=True)
    rhythm_id = db.Column(db.Integer, db.ForeignKey('rhythm.id'), nullable=True)
    # stimmverlauf
    has_melody = db.Column(db.Boolean, default=False)
    melody_form_id = db.Column(db.Integer, db.ForeignKey('melodieform.id'), nullable=True)
    intervallik_id = db.Column(db.Integer, db.ForeignKey('intervallik.id'), nullable=True)
    # Einsatz der Stimme
    share_id = db.Column(db.Integer, db.ForeignKey('anteil.id'), nullable=True)
    occurence_in_part_id = db.Column(db.Integer, db.ForeignKey('auftreten_werkausschnitt.id'), nullable=True)
    composition_id = db.Column(db.Integer, db.ForeignKey('composition.id'), nullable=True)
    rendition_id = db.Column(db.Integer, db.ForeignKey('rendition.id'), nullable=True)
    citations_id = db.Column(db.Integer, db.ForeignKey('citations.id'), nullable=True)

    subpart = db.relationship(SubPart, lazy='select', backref=db.backref('voices', single_parent=True, cascade="all, delete-orphan"))
    _instrumentation = db.relationship('Instrumentation', lazy='subquery', single_parent=True, cascade="all, delete-orphan")  # type: Instrumentation
    satz = db.relationship(Satz, single_parent=True, cascade="all, delete-orphan")
    rhythm = db.relationship(Rhythm, single_parent=True, cascade="all, delete-orphan")
    # stimmverlauf
    melody_form = db.relationship(Melodieform)
    intervallik = db.relationship(Intervallik)
    # Einsatz der Stimme
    share = db.relationship(Anteil)
    occurence_in_part = db.relationship(AuftretenWerkausschnitt)
    composition = db.relationship(Composition, single_parent=True, cascade="all, delete-orphan")
    rendition = db.relationship(Rendition, single_parent=True, cascade="all, delete-orphan")
    citations = db.relationship(Citations, single_parent=True, cascade="all, delete-orphan")

    _subquery_load = ['satz', 'rhythm', 'composition', 'rendition', 'citations']

    def __init__(self, subpart: Union[int, SubPart], name: str, **kwargs):
        if isinstance(subpart, SubPart):
            self.subpart = subpart
        else:
            self.subpart = SubPart.get_by_id(subpart)
        self.name = name

        self._instrumentation = Instrumentation()

    @property
    def instrumentation(self):
        return self._instrumentation.instruments

    @instrumentation.setter
    def instrumentation(self, data: list):
        self._instrumentation.instruments = data

    @property
    def musicial_function(self):
        return [mapping.musikalische_funktion for mapping in self._musicial_function]

    @musicial_function.setter
    def musicial_function(self, musicial_function_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.musikalische_funktion.id: mapping for mapping in self._musicial_function}
        self.update_list(musicial_function_list, old_items, MusikalischeFunktionToVoice,
                         MusikalischeFunktion, 'musikalische_funktion')

    @property
    def ornaments(self):
        return [mapping.verzierung for mapping in self._ornaments]

    @ornaments.setter
    def ornaments(self, ornaments_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.verzierung.id: mapping for mapping in self._ornaments}
        self.update_list(ornaments_list, old_items, VerzierungToVoice,
                         Verzierung, 'verzierung')

    @property
    def dominant_note_values(self):
        return [mapping.notenwert for mapping in self._dominant_note_values]

    @dominant_note_values.setter
    def dominant_note_values(self, dominant_note_values_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.notenwert.id: mapping for mapping in self._dominant_note_values}
        self.update_list(dominant_note_values_list, old_items, NotenwertToVoice,
                         Notenwert, 'notenwert')

    @property
    def musicial_figures(self):
        return [mapping.musikalische_wendung for mapping in self._musicial_figures]

    @musicial_figures.setter
    def musicial_figures(self, musicial_figures_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.musikalische_wendung.id: mapping for mapping in self._musicial_figures}
        self.update_list(musicial_figures_list, old_items, MusikalischeWendungToVoice,
                         MusikalischeWendung, 'musikalische_wendung')


class MusikalischeWendungToVoice(db.Model):
    voice_id = db.Column(db.Integer, db.ForeignKey('voice.id'), primary_key=True)
    musikalische_wendung_id = db.Column(db.Integer, db.ForeignKey('musikalische_wendung.id'), primary_key=True)

    voice = db.relationship(Voice, backref=db.backref('_musicial_figures', lazy='joined', single_parent=True, cascade='all, delete-orphan'))
    musikalische_wendung = db.relationship('MusikalischeWendung')

    def __init__(self, voice, musikalische_wendung, **kwargs):
        self.voice = voice
        self.musikalische_wendung = musikalische_wendung


class MusikalischeFunktionToVoice(db.Model):
    voice_id = db.Column(db.Integer, db.ForeignKey('voice.id'), primary_key=True)
    musikalische_funktion_id = db.Column(db.Integer, db.ForeignKey('musikalische_funktion.id'), primary_key=True)

    voice = db.relationship(Voice, backref=db.backref('_musicial_function', lazy='joined'))
    musikalische_funktion = db.relationship('MusikalischeFunktion')

    def __init__(self, voice, musikalische_funktion, **kwargs):
        self.voice = voice
        self.musikalische_funktion = musikalische_funktion


class VerzierungToVoice(db.Model):
    voice_id = db.Column(db.Integer, db.ForeignKey('voice.id'), primary_key=True)
    verzierung_id = db.Column(db.Integer, db.ForeignKey('verzierung.id'), primary_key=True)

    voice = db.relationship(Voice, backref=db.backref('_ornaments', lazy='joined', single_parent=True, cascade='all, delete-orphan'))
    verzierung = db.relationship('Verzierung')

    def __init__(self, voice, verzierung, **kwargs):
        self.voice = voice
        self.verzierung = verzierung


class NotenwertToVoice(db.Model):
    voice_id = db.Column(db.Integer, db.ForeignKey('voice.id'), primary_key=True)
    notenwert_id = db.Column(db.Integer, db.ForeignKey('notenwert.id'), primary_key=True)

    voice = db.relationship(Voice, backref=db.backref('_dominant_note_values', lazy='joined', single_parent=True, cascade='all, delete-orphan'))
    notenwert = db.relationship('Notenwert')

    def __init__(self, voice, notenwert, **kwargs):
        self.voice = voice
        self.notenwert = notenwert


class RelatedVoices(db.Model, GetByID, UpdateableModelMixin):

    _normal_attributes = (('type_of_relationship', VoiceToVoiceRelation), ('related_voice', Voice))
    _reference_only_attributes = ('related_voice', )


    id = db.Column(db.Integer, primary_key=True)
    voice_id = db.Column(db.Integer, db.ForeignKey('voice.id'))
    related_voice_id = db.Column(db.Integer, db.ForeignKey('voice.id'))
    type_of_relationship_id = db.Column(db.Integer, db.ForeignKey('voice_to_voice_relation.id'))

    voice = db.relationship(Voice, backref=db.backref('_related_voices', lazy='joined', single_parent=True, cascade='all, delete-orphan'),
                            foreign_keys=[voice_id])
    related_voice = db.relationship('Voice', foreign_keys=[related_voice_id])
    type_of_relationship = db.relationship('VoiceToVoiceRelation')

    def __init__(self, voice, **kwargs):
        self.voice = voice
        if kwargs:
            self.update(kwargs)
