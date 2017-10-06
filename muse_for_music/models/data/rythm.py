from ... import db
from ..taxonomies import Taktart, Rhythmustyp, RhythmischesPhaenomen
from ..helper_classes import GetByID, UpdateListMixin
from typing import Union, Sequence, List


class Rythm(db.Model, GetByID, UpdateListMixin):
    __tablename__ = 'rythm'
    id = db.Column(db.Integer, primary_key=True)
    polymetric = db.Column(db.Boolean, server_default=db.text('FALSE'))

    @property
    def measure_times(self):
        return [mapping.taktart for mapping in self._measure_times]

    @measure_times.setter
    def measure_times(self, measure_times_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.taktart.id: mapping for mapping in self._measure_times}
        self.update_list(measure_times_list, old_items, TaktartToRythm,
                         Taktart, 'taktart')

    @property
    def rythm_types(self):
        return [mapping.rhythmustyp for mapping in self._rythm_types]

    @rythm_types.setter
    def rythm_types(self, rythm_types_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.rhythmustyp.id: mapping for mapping in self._rythm_types}
        self.update_list(rythm_types_list, old_items, RhythmustypToRythm,
                         Rhythmustyp, 'rhythmustyp')

    @property
    def rythmic_phenomenons(self):
        return [mapping.rhythmisches_phaenomen for mapping in self._rythmic_phenomenons]

    @rythmic_phenomenons.setter
    def rythmic_phenomenons(self, rythmic_phenomenons_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.rhythmisches_phaenomen.id: mapping for mapping in self._rythmic_phenomenons}
        self.update_list(rythmic_phenomenons_list, old_items, RhythmischesPhaenomenToRythm,
                         RhythmischesPhaenomen, 'rhythmisches_phaenomen')


class TaktartToRythm(db.Model):
    rythm_id = db.Column(db.Integer, db.ForeignKey('rythm.id'), primary_key=True)
    taktart_id = db.Column(db.Integer, db.ForeignKey('taktart.id'), primary_key=True)

    rythm = db.relationship(Rythm, backref=db.backref('_measure_times', lazy='joined'))
    taktart = db.relationship('Taktart')

    def __init__(self, rythm, taktart):
        self.rythm = rythm
        self.taktart = taktart


class RhythmustypToRythm(db.Model):
    rythm_id = db.Column(db.Integer, db.ForeignKey('rythm.id'), primary_key=True)
    rhythmustyp_id = db.Column(db.Integer, db.ForeignKey('rhythmustyp.id'), primary_key=True)

    rythm = db.relationship(Rythm, backref=db.backref('_rythm_types', lazy='joined'))
    rhythmustyp = db.relationship('Rhythmustyp')

    def __init__(self, rythm, rhythmustyp):
        self.rythm = rythm
        self.rhythmustyp = rhythmustyp


class RhythmischesPhaenomenToRythm(db.Model):
    rythm_id = db.Column(db.Integer, db.ForeignKey('rythm.id'), primary_key=True)
    rhythmisches_phaenomen_id = db.Column(db.Integer, db.ForeignKey('rhythmisches_phaenomen.id'), primary_key=True)

    rythm = db.relationship(Rythm, backref=db.backref('_rythmic_phenomenons', lazy='joined'))
    rhythmisches_phaenomen = db.relationship('RhythmischesPhaenomen')

    def __init__(self, rythm, rhythmisches_phaenomen):
        self.rythm = rythm
        self.rhythmisches_phaenomen = rhythmisches_phaenomen
