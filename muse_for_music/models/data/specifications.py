from ... import db
from ..taxonomies import SpecAnteil, SpecAuftreten, SpecInstrument
from ..helper_classes import GetByID, UpdateListMixin, UpdateableModelMixin

from typing import Union, Sequence, List


class Specifications (db.Model, GetByID, UpdateListMixin, UpdateableModelMixin):

    _normal_attributes = (('spezifikation_anteil', SpecAnteil),
                          ('spezifikation_auftreten', SpecAuftreten))

    _list_attributes = (('spezifikation_instrument'))

    __tablename__ = 'specifications'
    id = db.Column(db.Integer, primary_key=True)
    spezifikation_anteil_id = db.Column(db.Integer, db.ForeignKey(SpecAnteil.id), nullable=True)
    spezifikation_auftreten_id = db.Column(db.Integer, db.ForeignKey(SpecAuftreten.id), nullable=True)

    spezefikation_anteil = db.relationship(SpecAnteil, lazy='joined')
    spezifikation_auftreten = db.relationship(SpecAuftreten, lazy='joined')

    @property
    def spezifikation_instrument(self):
        return [mapping.spezifikation_instrument for mapping in self._spezifikation_instrument]

    @spezifikation_instrument.setter
    def spezifikation_instrument(self, spezifikation_instrument_list:Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.spezifikation_instrument.id: mapping for mapping in self._spezifikation_instrument}
        self.update_list(spezifikation_instrument_list, old_items, SpecInstrumentToSpecifications,
                        SpecInstrument, 'spezifikation_instrument')


class SpecInstrumentToSpecifications(db.Model):
    specifications_id = db.Column(db.Integer, db.ForeignKey('specifications.id'), primary_key=True)
    spezifikation_instrument_id = db.Column(db.Integer, db.ForeignKey('spezifikation_instrument.id'), primary_key=True)

    specifications = db.relationship(Specifications, backref=db.backref('_spezifikation_instrument', lazy='joined', single_parent=True, cascade="all, delete-orphan"))
    spezifikation_instrument = db.relationship('SpecInstrument')

    def __init__(self, specifications, spezifikation_instrument, **kwargs):
        self.specifications = specifications
        self.spezifikation_instrument = spezifikation_instrument