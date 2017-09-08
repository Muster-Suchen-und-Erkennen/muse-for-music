from typing import Union, Sequence

from ... import db
from ..taxonomies import Instrument
from ..helper_classes import GetByID, UpdateListMixin


class Instrumentation(db.Model, GetByID, UpdateListMixin):
    id = db.Column(db.Integer, primary_key=True)

    @property
    def instruments(self):
        return [mapping.instrument for mapping in self._instruments]

    def update(self, instrument_list: Union[Sequence[int], Sequence[dict]]):

        old_items = {mapping.instrument.id: mapping for mapping in self._instruments}
        self.update_list(instrument_list, old_items, InstumentationToInstrument,
                         Instrument, 'instrument')


class InstumentationToInstrument(db.Model):
    instrumentation_id = db.Column(db.Integer, db.ForeignKey('instrumentation.id'), primary_key=True)
    instrument_id = db.Column(db.Integer, db.ForeignKey('instrument.id'), primary_key=True)

    instrumentation = db.relationship(Instrumentation, backref=db.backref('_instruments', lazy='joined'))
    instrument = db.relationship('Instrument')

    def __init__(self, instrumentation, instrument):
        self.instrumentation = instrumentation
        self.instrument = instrument
