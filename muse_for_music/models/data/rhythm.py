from ... import db
from ..taxonomies import Taktart, Rhythmustyp, RhythmischesPhaenomen
from ..helper_classes import GetByID, UpdateListMixin, UpdateableModelMixin
from typing import Union, Sequence, List


class Rhythm(db.Model, GetByID, UpdateListMixin, UpdateableModelMixin):

    _normal_attributes = (('polymetric', bool), )
    _list_attributes = ('rhythmic_phenomenons', 'measure_times', 'rhythm_types')

    __tablename__ = 'rhythm'
    id = db.Column(db.Integer, primary_key=True)
    polymetric = db.Column(db.Boolean, default=False)

    @property
    def measure_times(self):
        return [mapping.taktart for mapping in self._measure_times]

    @measure_times.setter
    def measure_times(self, measure_times_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.taktart.id: mapping for mapping in self._measure_times}
        self.update_list(measure_times_list, old_items, TaktartToRhythm,
                         Taktart, 'taktart')

    @property
    def rhythm_types(self):
        return [mapping.rhythmustyp for mapping in self._rhythm_types]

    @rhythm_types.setter
    def rhythm_types(self, rhythm_types_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.rhythmustyp.id: mapping for mapping in self._rhythm_types}
        self.update_list(rhythm_types_list, old_items, RhythmustypToRhythm,
                         Rhythmustyp, 'rhythmustyp')

    @property
    def rhythmic_phenomenons(self):
        return [mapping.rhythmisches_phaenomen for mapping in self._rhythmic_phenomenons]

    @rhythmic_phenomenons.setter
    def rhythmic_phenomenons(self, rhythmic_phenomenons_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.rhythmisches_phaenomen.id: mapping for mapping in self._rhythmic_phenomenons}
        self.update_list(rhythmic_phenomenons_list, old_items, RhythmischesPhaenomenToRhythm,
                         RhythmischesPhaenomen, 'rhythmisches_phaenomen')


class TaktartToRhythm(db.Model):
    rhythm_id = db.Column(db.Integer, db.ForeignKey('rhythm.id'), primary_key=True)
    taktart_id = db.Column(db.Integer, db.ForeignKey('taktart.id'), primary_key=True)

    rhythm = db.relationship(Rhythm, backref=db.backref('_measure_times', lazy='joined'))
    taktart = db.relationship('Taktart')

    def __init__(self, rhythm, taktart, **kwargs):
        self.rhythm = rhythm
        self.taktart = taktart


class RhythmustypToRhythm(db.Model):
    rhythm_id = db.Column(db.Integer, db.ForeignKey('rhythm.id'), primary_key=True)
    rhythmustyp_id = db.Column(db.Integer, db.ForeignKey('rhythmustyp.id'), primary_key=True)

    rhythm = db.relationship(Rhythm, backref=db.backref('_rhythm_types', lazy='joined', single_parent=True, cascade="all, delete-orphan"))
    rhythmustyp = db.relationship('Rhythmustyp')

    def __init__(self, rhythm, rhythmustyp, **kwargs):
        self.rhythm = rhythm
        self.rhythmustyp = rhythmustyp


class RhythmischesPhaenomenToRhythm(db.Model):
    rhythm_id = db.Column(db.Integer, db.ForeignKey('rhythm.id'), primary_key=True)
    rhythmisches_phaenomen_id = db.Column(db.Integer, db.ForeignKey('rhythmisches_phaenomen.id'), primary_key=True)

    rhythm = db.relationship(Rhythm, backref=db.backref('_rhythmic_phenomenons', lazy='joined', single_parent=True, cascade="all, delete-orphan"))
    rhythmisches_phaenomen = db.relationship('RhythmischesPhaenomen')

    def __init__(self, rhythm, rhythmisches_phaenomen, **kwargs):
        self.rhythm = rhythm
        self.rhythmisches_phaenomen = rhythmisches_phaenomen
