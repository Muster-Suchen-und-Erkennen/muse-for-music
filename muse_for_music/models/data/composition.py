from ... import db
from ..taxonomies import Verarbeitungstechnik, Intervall, BewegungImTonraum
from ..helper_classes import GetByID, UpdateListMixin, UpdateableModelMixin

from typing import Union, Sequence, List


class Composition(db.Model, GetByID, UpdateListMixin, UpdateableModelMixin):

    _normal_attributes = (
        ('nr_repetitions_1_2', int),
        ('nr_repetitions_3_4', int),
        ('nr_repetitions_5_6', int),
        ('nr_repetitions_5_6', int)
    )
    _list_attributes = ('sequences', 'composition_techniques')

    __tablename__ = 'composition'
    id = db.Column(db.Integer, primary_key=True)

    nr_repetitions_1_2 = db.Column(db.Integer, server_default=db.text("'0'"))
    nr_repetitions_3_4 = db.Column(db.Integer, server_default=db.text("'0'"))
    nr_repetitions_5_6 = db.Column(db.Integer, server_default=db.text("'0'"))
    nr_repetitions_7_10 = db.Column(db.Integer, server_default=db.text("'0'"))

    @property
    def composition_techniques(self):
        return [mapping.verarbeitungstechnik for mapping in self._techniques]

    @composition_techniques.setter
    def composition_techniques(self, techniques_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.verarbeitungstechnik.id: mapping for mapping in self._techniques}
        self.update_list(techniques_list, old_items, CompositionTechniqueToComposition,
                         Verarbeitungstechnik, 'verarbeitungstechnik')

    @property
    def sequences(self):
        return self._sequences

    @sequences.setter
    def sequences(self, sequence_list: Sequence[dict]):
        old_items = {seq.id: seq for seq in self._sequences}
        to_add = []  # type: List[MusicialSequence]

        for sequence in sequence_list:
            sequence_id = sequence.get('id')
            if sequence_id in old_items:
                old_items[sequence_id].update(**sequence)
                del old_items[sequence_id]
            else:
                to_add.append(MusicialSequence(self, **sequence))

        for seq in to_add:
            db.session.add(seq)
        to_delete = list(old_items.values())  # type: List[MusicialSequence]
        for seq in to_delete:
            db.session.delete(seq)


class CompositionTechniqueToComposition(db.Model):
    composition_id = db.Column(db.Integer, db.ForeignKey('composition.id'), primary_key=True)
    verarbeitungstechnik_id = db.Column(db.Integer, db.ForeignKey('verarbeitungstechnik.id'), primary_key=True)

    composition = db.relationship(Composition, backref=db.backref('_techniques', lazy='joined', single_parent=True, cascade="all, delete-orphan"))
    verarbeitungstechnik = db.relationship('Verarbeitungstechnik')

    def __init__(self, composition, verarbeitungstechnik, **kwargs):
        self.composition = composition
        self.verarbeitungstechnik = verarbeitungstechnik


class MusicialSequence(db.Model, GetByID):
    __tablename__ = 'sequence'
    id = db.Column(db.Integer, primary_key=True)
    composition_id = db.Column(db.Integer, db.ForeignKey('composition.id'))
    tonal_corrected = db.Column(db.Boolean, default=False)
    exact_repetition = db.Column(db.Boolean, default=False)
    starting_interval_id = db.Column(db.Integer, db.ForeignKey('intervall.id'))
    flow_id = db.Column(db.Integer, db.ForeignKey('bewegung_im_tonraum.id'))
    beats = db.Column(db.Integer)

    starting_interval = db.relationship(Intervall, lazy='joined')
    flow = db.relationship(BewegungImTonraum, lazy='joined')
    composition = db.relationship(Composition, backref=db.backref('_sequences', lazy='joined', single_parent=True, cascade="all, delete-orphan"))

    def __init__(self, composition, starting_interval, flow, beats: int, tonal_corrected: bool=False, exact_repetition: bool=False, **kwargs):
        if isinstance(composition, Composition):
            self.composition = composition
        else:
            self.composition = Composition.get_by_id(composition)
        self.update(starting_interval, flow, beats, tonal_corrected, exact_repetition)

    def update(self, starting_interval, flow, beats: int, tonal_corrected: bool, exact_repetition: bool, **kwargs):
        self.starting_interval = Intervall.get_by_id_or_dict(starting_interval)
        self.flow = BewegungImTonraum.get_by_id_or_dict(flow)
        self.beats = beats
        self.tonal_corrected = tonal_corrected
        self.exact_repetition = exact_repetition
