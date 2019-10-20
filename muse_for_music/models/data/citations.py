from ... import db
from ..taxonomies import Zitat, Epoche, Gattung, Instrument, Programmgegenstand, Tonmalerei
from .people import Person
from .opus import Opus
from ..helper_classes import GetByID, UpdateListMixin, UpdateableModelMixin

from typing import Union, Sequence, List


class Citations(db.Model, GetByID, UpdateListMixin, UpdateableModelMixin):

    _list_attributes = ('opus_citations',
                        'instrument_citations',
                        'epoch_citations',
                        'gattung_citations',
                        'tonmalerei_citations',
                        'program_citations',
                        'composer_citations')

    __tablename__ = 'citations'
    id = db.Column(db.Integer, primary_key=True)

    @property
    def opus_citations(self):
        return self._opus_citations

    @opus_citations.setter
    def opus_citations(self, opus_citations_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.id: mapping for mapping in self._opus_citations}
        self.update_list(opus_citations_list, old_items, OpusCitation)

    @property
    def epoch_citations(self):
        return [mapping.epoche for mapping in self._epoch_citations]

    @epoch_citations.setter
    def epoch_citations(self, epoch_citations_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.epoche.id: mapping for mapping in self._epoch_citations}
        self.update_list(epoch_citations_list, old_items, EpocheToCitations,
                         Epoche, 'epoche')

    @property
    def gattung_citations(self):
        return [mapping.gattung for mapping in self._gattung_citations]

    @gattung_citations.setter
    def gattung_citations(self, gattung_citations_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.gattung.id: mapping for mapping in self._gattung_citations}
        self.update_list(gattung_citations_list, old_items, GattungToCitations,
                         Gattung, 'gattung')

    @property
    def composer_citations(self):
        return [mapping.person for mapping in self._composer_citations]

    @composer_citations.setter
    def composer_citations(self, composer_citations_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.person.id: mapping for mapping in self._composer_citations}
        self.update_list(composer_citations_list, old_items, PersonToCitations,
                         Person, 'person')

    @property
    def instrument_citations(self):
        return [mapping.instrument for mapping in self._instrument_citations]

    @instrument_citations.setter
    def instrument_citations(self, instrument_citations_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.instrument.id: mapping for mapping in self._instrument_citations}
        self.update_list(instrument_citations_list, old_items, InstrumentToCitations,
                         Instrument, 'instrument')

    @property
    def program_citations(self):
        return [mapping.programmgegenstand for mapping in self._program_citations]

    @program_citations.setter
    def program_citations(self, program_citations_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.programmgegenstand.id: mapping for mapping in self._program_citations}
        self.update_list(program_citations_list, old_items, ProgrammgegenstandToCitations,
                         Programmgegenstand, 'programmgegenstand')

    @property
    def tonmalerei_citations(self):
        return [mapping.tonmalerei for mapping in self._tonmalerei_citations]

    @tonmalerei_citations.setter
    def tonmalerei_citations(self, tonmalerei_citations_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.tonmalerei.id: mapping for mapping in self._tonmalerei_citations}
        self.update_list(tonmalerei_citations_list, old_items, TonmalereiToCitations,
                         Tonmalerei, 'tonmalerei')


class OpusCitation(db.Model, GetByID, UpdateableModelMixin):

    _normal_attributes = (('citation_type', Zitat), ('opus', Opus))
    _reference_only_attributes = ('opus', )

    id = db.Column(db.Integer, primary_key=True)
    citations_id = db.Column(db.Integer, db.ForeignKey('citations.id'))
    opus_id = db.Column(db.Integer, db.ForeignKey('opus.id'), nullable=True)
    citation_type_id = db.Column(db.Integer, db.ForeignKey('zitat.id'))

    citations = db.relationship(Citations, backref=db.backref('_opus_citations', lazy='joined', single_parent=True, cascade="all, delete-orphan"))
    opus = db.relationship('Opus')
    citation_type = db.relationship(Zitat)

    def __init__(self, citations, **kwargs):
        self.citations = citations
        if kwargs:
            self.update(kwargs)



class EpocheToCitations(db.Model):
    citations_id = db.Column(db.Integer, db.ForeignKey('citations.id'), primary_key=True)
    epoche_id = db.Column(db.Integer, db.ForeignKey('epoche.id'), primary_key=True)

    citations = db.relationship(Citations, backref=db.backref('_epoch_citations', lazy='joined', single_parent=True, cascade="all, delete-orphan"))
    epoche = db.relationship('Epoche')

    def __init__(self, citations, epoche):
        self.citations = citations
        self.epoche = epoche


class GattungToCitations(db.Model):
    citations_id = db.Column(db.Integer, db.ForeignKey('citations.id'), primary_key=True)
    gattung_id = db.Column(db.Integer, db.ForeignKey('gattung.id'), primary_key=True)

    citations = db.relationship(Citations, backref=db.backref('_gattung_citations', lazy='joined', single_parent=True, cascade="all, delete-orphan"))
    gattung = db.relationship('Gattung')

    def __init__(self, citations, gattung):
        self.citations = citations
        self.gattung = gattung


class PersonToCitations(db.Model):
    _reference_only_attributes = ('person', )

    citations_id = db.Column(db.Integer, db.ForeignKey('citations.id'), primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), primary_key=True)

    citations = db.relationship(Citations, backref=db.backref('_composer_citations', lazy='joined', single_parent=True, cascade="all, delete-orphan"))
    person = db.relationship('Person')

    def __init__(self, citations, person):
        self.citations = citations
        self.person = person


class InstrumentToCitations(db.Model):
    citations_id = db.Column(db.Integer, db.ForeignKey('citations.id'), primary_key=True)
    instrument_id = db.Column(db.Integer, db.ForeignKey('instrument.id'), primary_key=True)

    citations = db.relationship(Citations, backref=db.backref('_instrument_citations', lazy='joined', single_parent=True, cascade="all, delete-orphan"))
    instrument = db.relationship('Instrument')

    def __init__(self, citations, instrument):
        self.citations = citations
        self.instrument = instrument


class ProgrammgegenstandToCitations(db.Model):
    citations_id = db.Column(db.Integer, db.ForeignKey('citations.id'), primary_key=True)
    programmgegenstand_id = db.Column(db.Integer, db.ForeignKey('programmgegenstand.id'), primary_key=True)

    citations = db.relationship(Citations, backref=db.backref('_program_citations', lazy='joined', single_parent=True, cascade="all, delete-orphan"))
    programmgegenstand = db.relationship('Programmgegenstand')

    def __init__(self, citations, programmgegenstand):
        self.citations = citations
        self.programmgegenstand = programmgegenstand


class TonmalereiToCitations(db.Model):
    citations_id = db.Column(db.Integer, db.ForeignKey('citations.id'), primary_key=True)
    tonmalerei_id = db.Column(db.Integer, db.ForeignKey('tonmalerei.id'), primary_key=True)

    citations = db.relationship(Citations, backref=db.backref('_tonmalerei_citations', lazy='joined', single_parent=True, cascade="all, delete-orphan"))
    tonmalerei = db.relationship('Tonmalerei')

    def __init__(self, citations, tonmalerei):
        self.citations = citations
        self.tonmalerei = tonmalerei

