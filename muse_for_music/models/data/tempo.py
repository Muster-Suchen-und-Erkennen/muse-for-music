
from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin, UpdateListMixin
from ..taxonomies import TempoEinbettung, TempoEntwicklung, Tempo

from typing import Union, Sequence, Dict


class TempoContext(db.Model, GetByID, UpdateableModelMixin):

    _normal_attributes = (('tempo_trend_before', TempoEntwicklung),
                          ('tempo_context_before', TempoEinbettung),
                          ('tempo_trend_after', TempoEntwicklung),
                          ('tempo_context_after', TempoEinbettung))

    __tablename__ = 'tempo_context'
    id = db.Column(db.Integer, primary_key=True)

    tempo_context_before_id = db.Column(db.Integer, db.ForeignKey('tempo_einbettung.id'),
                                        nullable=True)
    tempo_context_after_id = db.Column(db.Integer, db.ForeignKey('tempo_einbettung.id'),
                                       nullable=True)
    tempo_trend_before_id = db.Column(db.Integer, db.ForeignKey('tempo_entwicklung.id'),
                                      nullable=True)
    tempo_trend_after_id = db.Column(db.Integer, db.ForeignKey('tempo_entwicklung.id'),
                                     nullable=True)

    tempo_context_before = db.relationship(TempoEinbettung, foreign_keys=[tempo_context_before_id])
    tempo_context_after = db.relationship(TempoEinbettung, foreign_keys=[tempo_context_after_id])
    tempo_trend_before = db.relationship(TempoEntwicklung, foreign_keys=[tempo_trend_before_id])
    tempo_trend_after = db.relationship(TempoEntwicklung, foreign_keys=[tempo_trend_after_id])


class TempoGroup(db.Model, GetByID, UpdateableModelMixin, UpdateListMixin):

    _list_attributes = ('tempo_markings', 'tempo_changes')

    __tablename__ = 'tempo_group'
    id = db.Column(db.Integer, primary_key=True)

    @property
    def tempo_markings(self):
        return [mapping.tempo for mapping in self._tempo_markings]

    @tempo_markings.setter
    def tempo_markings(self, tempo_markings_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.tempo.id: mapping for mapping in self._tempo_markings}
        self.update_list(tempo_markings_list, old_items, TempoToTempoGroup,
                         Tempo, 'tempo')

    @property
    def tempo_changes(self):
        return [mapping.tempo_entwicklung for mapping in self._tempo_changes]

    @tempo_changes.setter
    def tempo_changes(self, tempo_changes_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.tempo_entwicklung.id: mapping for mapping in self._tempo_changes}
        self.update_list(tempo_changes_list, old_items, TempoEntwicklungToTempoGroup,
                         TempoEntwicklung, 'tempo_entwicklung')


class TempoToTempoGroup(db.Model):
    tempo_group_id = db.Column(db.Integer, db.ForeignKey('tempo_group.id'), primary_key=True)
    tempo_id = db.Column(db.Integer, db.ForeignKey('tempo.id'), primary_key=True)

    tempo_group = db.relationship(TempoGroup, backref=db.backref('_tempo_markings', lazy='joined', single_parent=True, cascade='all, delete-orphan'))
    tempo = db.relationship('Tempo')

    def __init__(self, tempo_group, tempo, **kwargs):
        self.tempo_group = tempo_group
        self.tempo = tempo


class TempoEntwicklungToTempoGroup(db.Model):
    tempo_group_id = db.Column(db.Integer, db.ForeignKey('tempo_group.id'), primary_key=True)
    tempo_entwicklung_id = db.Column(db.Integer, db.ForeignKey('tempo_entwicklung.id'), primary_key=True)

    tempo_group = db.relationship(TempoGroup, backref=db.backref('_tempo_changes', lazy='joined', single_parent=True, cascade='all, delete-orphan'))
    tempo_entwicklung = db.relationship('TempoEntwicklung')

    def __init__(self, tempo_group, tempo_entwicklung, **kwargs):
        self.tempo_group = tempo_group
        self.tempo_entwicklung = tempo_entwicklung
