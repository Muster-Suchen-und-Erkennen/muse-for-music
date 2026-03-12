from typing import Sequence, Union

from sqlalchemy.orm import Mapped, MappedColumn, relationship

from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin, UpdateListMixin
from ..taxonomies import (
    Instrument,
    InstrumentierungEinbettungQualitaet,
    InstrumentierungEinbettungQuantitaet,
)


class Instrumentation(db.Model, GetByID, UpdateListMixin):
    id = db.Column(db.Integer, primary_key=True)

    # backref
    _instruments: Mapped[list["InstumentationToInstrument"]] = relationship(
        lambda: InstumentationToInstrument,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="instrumentation",
    )

    @property
    def instruments(self):
        return [mapping.instrument for mapping in self._instruments]

    @instruments.setter
    def instruments(self, instrument_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.instrument.id: mapping for mapping in self._instruments}
        self.update_list(
            instrument_list,
            old_items,
            InstumentationToInstrument,
            Instrument,
            "instrument",
        )


class InstumentationToInstrument(db.Model):
    instrumentation_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Instrumentation.id), primary_key=True
    )
    instrument_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Instrument.id), primary_key=True
    )

    instrumentation: Mapped[Instrumentation] = relationship(
        Instrumentation, back_populates="_instruments"
    )
    instrument: Mapped[Instrument] = relationship(Instrument)

    def __init__(self, instrumentation, instrument, **kwargs):
        self.instrumentation = instrumentation
        self.instrument = instrument


class InstrumentationContext(db.Model, GetByID, UpdateableModelMixin):
    __tablename__ = "instrumentation_context"

    _normal_attributes = (
        ("instrumentation_quantity_before", InstrumentierungEinbettungQuantitaet),
        ("instrumentation_quality_before", InstrumentierungEinbettungQualitaet),
        ("instrumentation_quantity_after", InstrumentierungEinbettungQuantitaet),
        ("instrumentation_quality_after", InstrumentierungEinbettungQualitaet),
    )

    id = db.Column(db.Integer, primary_key=True)
    instr_quantity_before_id: MappedColumn[int | None] = db.Column(
        db.Integer,
        db.ForeignKey(InstrumentierungEinbettungQuantitaet.id),
        nullable=True,
    )
    instr_quantity_after_id: MappedColumn[int | None] = db.Column(
        db.Integer,
        db.ForeignKey(InstrumentierungEinbettungQuantitaet.id),
        nullable=True,
    )
    instr_quality_before_id: MappedColumn[int | None] = db.Column(
        db.Integer,
        db.ForeignKey(InstrumentierungEinbettungQualitaet.id),
        nullable=True,
    )
    instr_quality_after_id: MappedColumn[int | None] = db.Column(
        db.Integer,
        db.ForeignKey(InstrumentierungEinbettungQualitaet.id),
        nullable=True,
    )

    instrumentation_quantity_before: Mapped[InstrumentierungEinbettungQuantitaet] = (
        relationship(
            InstrumentierungEinbettungQuantitaet,
            foreign_keys=[instr_quantity_before_id],
        )
    )
    instrumentation_quantity_after: Mapped[InstrumentierungEinbettungQuantitaet] = (
        relationship(
            InstrumentierungEinbettungQuantitaet,
            foreign_keys=[instr_quantity_after_id],
        )
    )
    instrumentation_quality_before: Mapped[InstrumentierungEinbettungQualitaet] = (
        relationship(
            InstrumentierungEinbettungQualitaet,
            foreign_keys=[instr_quality_before_id],
        )
    )
    instrumentation_quality_after: Mapped[InstrumentierungEinbettungQualitaet] = (
        relationship(
            InstrumentierungEinbettungQualitaet,
            foreign_keys=[instr_quality_after_id],
        )
    )
