from typing import Union, Sequence

from ... import db
from ..taxonomies import Instrument, InstrumentierungEinbettungQualitaet, \
                         InstrumentierungEinbettungQuantitaet
from ..helper_classes import GetByID, UpdateListMixin


class Instrumentation(db.Model, GetByID, UpdateListMixin):
    id = db.Column(db.Integer, primary_key=True)

    @property
    def instruments(self):
        return [mapping.instrument for mapping in self._instruments]

    @instruments.setter
    def instruments(self, instrument_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.instrument.id: mapping for mapping in self._instruments}
        self.update_list(instrument_list, old_items, InstumentationToInstrument,
                         Instrument, 'instrument')


class InstumentationToInstrument(db.Model):
    instrumentation_id = db.Column(db.Integer, db.ForeignKey('instrumentation.id'), primary_key=True)
    instrument_id = db.Column(db.Integer, db.ForeignKey('instrument.id'), primary_key=True)

    instrumentation = db.relationship(Instrumentation, backref=db.backref('_instruments', lazy='joined'))
    instrument = db.relationship('Instrument')

    def __init__(self, instrumentation, instrument, **kwargs):
        self.instrumentation = instrumentation
        self.instrument = instrument


class InstrumentationContext(db.Model, GetByID):
    __tablename__ = 'instrumentation_context'
    id = db.Column(db.Integer, primary_key=True)
    instr_quantity_before_id = db.Column(db.Integer,
                                         db.ForeignKey('instrumentierung_einbettung_quantitaet.id'),
                                         nullable=True)
    instr_quantity_after_id = db.Column(db.Integer,
                                        db.ForeignKey('instrumentierung_einbettung_quantitaet.id'),
                                        nullable=True)
    instr_quality_before_id = db.Column(db.Integer,
                                        db.ForeignKey('instrumentierung_einbettung_qualitaet.id'),
                                        nullable=True)
    instr_quality_after_id = db.Column(db.Integer,
                                       db.ForeignKey('instrumentierung_einbettung_qualitaet.id'),
                                       nullable=True)

    instrumentation_quantity_before = db.relationship(InstrumentierungEinbettungQuantitaet,
                                                      foreign_keys=[instr_quantity_before_id])
    instrumentation_quantity_after = db.relationship(InstrumentierungEinbettungQuantitaet,
                                                     foreign_keys=[instr_quantity_after_id])
    instrumentation_quality_before = db.relationship(InstrumentierungEinbettungQualitaet,
                                                     foreign_keys=[instr_quality_before_id])
    instrumentation_quality_after = db.relationship(InstrumentierungEinbettungQualitaet,
                                                    foreign_keys=[instr_quality_after_id])
