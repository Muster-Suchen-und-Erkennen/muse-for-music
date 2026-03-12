from typing import Sequence, Union

from sqlalchemy.orm import Mapped, MappedColumn, relationship

from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin, UpdateListMixin
from ..taxonomies import (
    Epoche,
    Gattung,
    Instrument,
    Programmgegenstand,
    Tonmalerei,
    Zitat,
)
from .opus import Opus
from .people import Person


class Citations(db.Model, GetByID, UpdateListMixin, UpdateableModelMixin):

    _list_attributes = (
        "opus_citations",
        "instrument_citations",
        "epoch_citations",
        "gattung_citations",
        "tonmalerei_citations",
        "program_citations",
        "composer_citations",
    )

    __tablename__ = "citations"
    id = db.Column(db.Integer, primary_key=True)

    # backrefs (defined here explicitly; populated by association tables below)
    _opus_citations: Mapped[list["OpusCitation"]] = relationship(
        lambda: OpusCitation,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="citations",
    )
    _epoch_citations: Mapped[list["EpocheToCitations"]] = relationship(
        lambda: EpocheToCitations,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="citations",
    )
    _gattung_citations: Mapped[list["GattungToCitations"]] = relationship(
        lambda: GattungToCitations,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="citations",
    )
    _composer_citations: Mapped[list["PersonToCitations"]] = relationship(
        lambda: PersonToCitations,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="citations",
    )
    _instrument_citations: Mapped[list["InstrumentToCitations"]] = relationship(
        lambda: InstrumentToCitations,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="citations",
    )
    _program_citations: Mapped[list["ProgrammgegenstandToCitations"]] = relationship(
        lambda: ProgrammgegenstandToCitations,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="citations",
    )
    _tonmalerei_citations: Mapped[list["TonmalereiToCitations"]] = relationship(
        lambda: TonmalereiToCitations,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="citations",
    )

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
        self.update_list(
            epoch_citations_list, old_items, EpocheToCitations, Epoche, "epoche"
        )

    @property
    def gattung_citations(self):
        return [mapping.gattung for mapping in self._gattung_citations]

    @gattung_citations.setter
    def gattung_citations(
        self, gattung_citations_list: Union[Sequence[int], Sequence[dict]]
    ):
        old_items = {mapping.gattung.id: mapping for mapping in self._gattung_citations}
        self.update_list(
            gattung_citations_list, old_items, GattungToCitations, Gattung, "gattung"
        )

    @property
    def composer_citations(self):
        return [mapping.person for mapping in self._composer_citations]

    @composer_citations.setter
    def composer_citations(
        self, composer_citations_list: Union[Sequence[int], Sequence[dict]]
    ):
        old_items = {mapping.person.id: mapping for mapping in self._composer_citations}
        self.update_list(
            composer_citations_list, old_items, PersonToCitations, Person, "person"
        )

    @property
    def instrument_citations(self):
        return [mapping.instrument for mapping in self._instrument_citations]

    @instrument_citations.setter
    def instrument_citations(
        self, instrument_citations_list: Union[Sequence[int], Sequence[dict]]
    ):
        old_items = {
            mapping.instrument.id: mapping for mapping in self._instrument_citations
        }
        self.update_list(
            instrument_citations_list,
            old_items,
            InstrumentToCitations,
            Instrument,
            "instrument",
        )

    @property
    def program_citations(self):
        return [mapping.programmgegenstand for mapping in self._program_citations]

    @program_citations.setter
    def program_citations(
        self, program_citations_list: Union[Sequence[int], Sequence[dict]]
    ):
        old_items = {
            mapping.programmgegenstand.id: mapping for mapping in self._program_citations
        }
        self.update_list(
            program_citations_list,
            old_items,
            ProgrammgegenstandToCitations,
            Programmgegenstand,
            "programmgegenstand",
        )

    @property
    def tonmalerei_citations(self):
        return [mapping.tonmalerei for mapping in self._tonmalerei_citations]

    @tonmalerei_citations.setter
    def tonmalerei_citations(
        self, tonmalerei_citations_list: Union[Sequence[int], Sequence[dict]]
    ):
        old_items = {
            mapping.tonmalerei.id: mapping for mapping in self._tonmalerei_citations
        }
        self.update_list(
            tonmalerei_citations_list,
            old_items,
            TonmalereiToCitations,
            Tonmalerei,
            "tonmalerei",
        )


class OpusCitation(db.Model, GetByID, UpdateableModelMixin):

    _normal_attributes = (("citation_type", Zitat), ("opus", Opus))
    _reference_only_attributes = ("opus",)

    id: MappedColumn[int] = db.Column(db.Integer, primary_key=True)
    citations_id: MappedColumn[int] = db.Column(db.Integer, db.ForeignKey(Citations.id))
    opus_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Opus.id), nullable=True
    )
    citation_type_id: MappedColumn[int] = db.Column(db.Integer, db.ForeignKey(Zitat.id))

    citations: Mapped[Citations] = relationship(
        Citations, back_populates="_opus_citations"
    )
    opus: Mapped[Opus] = relationship(Opus)
    citation_type: Mapped[Zitat] = relationship(Zitat)

    def __init__(self, citations, **kwargs):
        self.citations = citations
        if kwargs:
            self.update(kwargs)


class EpocheToCitations(db.Model):
    citations_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Citations.id), primary_key=True
    )
    epoche_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Epoche.id), primary_key=True
    )

    citations: Mapped[Citations] = relationship(
        Citations, back_populates="_epoch_citations"
    )
    epoche: Mapped[Epoche] = relationship(Epoche)

    def __init__(self, citations, epoche):
        self.citations = citations
        self.epoche = epoche


class GattungToCitations(db.Model):
    citations_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Citations.id), primary_key=True
    )
    gattung_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Gattung.id), primary_key=True
    )

    citations: Mapped[Citations] = relationship(
        Citations, back_populates="_gattung_citations"
    )
    gattung: Mapped[Gattung] = relationship(Gattung)

    def __init__(self, citations, gattung):
        self.citations = citations
        self.gattung = gattung


class PersonToCitations(db.Model):
    _reference_only_attributes = ("person",)

    citations_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Citations.id), primary_key=True
    )
    person_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Person.id), primary_key=True
    )

    citations: Mapped[Citations] = relationship(
        Citations, back_populates="_composer_citations"
    )
    person: Mapped[Person] = relationship(Person)

    def __init__(self, citations, person):
        self.citations = citations
        self.person = person


class InstrumentToCitations(db.Model):
    citations_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Citations.id), primary_key=True
    )
    instrument_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Instrument.id), primary_key=True
    )

    citations: Mapped[Citations] = relationship(
        Citations, back_populates="_instrument_citations"
    )
    instrument: Mapped[Instrument] = relationship(Instrument)

    def __init__(self, citations, instrument):
        self.citations = citations
        self.instrument = instrument


class ProgrammgegenstandToCitations(db.Model):
    citations_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Citations.id), primary_key=True
    )
    programmgegenstand_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Programmgegenstand.id), primary_key=True
    )

    citations: Mapped[Citations] = relationship(
        Citations, back_populates="_program_citations"
    )
    programmgegenstand: Mapped[Programmgegenstand] = relationship(Programmgegenstand)

    def __init__(self, citations, programmgegenstand):
        self.citations = citations
        self.programmgegenstand = programmgegenstand


class TonmalereiToCitations(db.Model):
    citations_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Citations.id), primary_key=True
    )
    tonmalerei_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Tonmalerei.id), primary_key=True
    )

    citations: Mapped[Citations] = relationship(
        Citations, back_populates="_tonmalerei_citations"
    )
    tonmalerei: Mapped[Tonmalerei] = relationship(Tonmalerei)

    def __init__(self, citations, tonmalerei):
        self.citations = citations
        self.tonmalerei = tonmalerei
