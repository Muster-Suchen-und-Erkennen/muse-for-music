
from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin
from ..taxonomies import Lautstaerke, LautstaerkeEinbettung, LautstaerkeZusatz, LautstaerkeEntwicklung

from typing import Union, Sequence, List


class Dynamic(db.Model, GetByID, UpdateableModelMixin):

    _list_attributes = ('dynamic_markings', 'dynamic_changes')

    __tablename__ = 'dynamic'
    id = db.Column(db.Integer, primary_key=True)

    @property
    def dynamic_changes(self):
        return [mapping.lautstaerke_entwicklung for mapping in self._dynamic_changes]

    @dynamic_changes.setter
    def dynamic_changes(self, dynamic_changes_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.lautstaerke_entwicklung.id: mapping for mapping in self._dynamic_changes}
        self.update_list(dynamic_changes_list, old_items, LautstaerkeEntwicklungToDynamic,
                         LautstaerkeEntwicklung, 'lautstaerke_entwicklung')

    @property
    def dynamic_markings(self):
        return self._dynamic_markings

    @dynamic_markings.setter
    def dynamic_markings(self, dynamic_markings_list: Sequence[dict]):
        old_items = {mark.id: mark for mark in self._dynamic_markings}
        to_add = []  # type: List[DynamicMarking]
        for dynamic_mark in dynamic_markings_list:
            dynamic_mark_id = dynamic_mark.get('id')
            if dynamic_mark_id in old_items:
                old_items[dynamic_mark_id].update(**dynamic_mark)
                del old_items[dynamic_mark_id]
            else:
                to_add.append(DynamicMarking(self, **dynamic_mark))

        for mark in to_add:
            db.session.add(mark)
        to_delete = list(old_items.values())  # type: List[DynamicMarking]
        for mark in to_delete:
            db.session.delete(mark)
        raise NotImplementedError


class DynamicContext(db.Model, GetByID):
    __tablename__ = 'dynamic_context'
    id = db.Column(db.Integer, primary_key=True)

    loudness_before_id = db.Column(db.Integer, db.ForeignKey('lautstaerke.id'),
                                   nullable=True)
    loudness_after_id = db.Column(db.Integer, db.ForeignKey('lautstaerke.id'),
                                  nullable=True)
    dynamic_trend_before_id = db.Column(db.Integer,
                                        db.ForeignKey('lautstaerke_einbettung.id'),
                                        nullable=True)
    dynamic_trend_after_id = db.Column(db.Integer,
                                       db.ForeignKey('lautstaerke_einbettung.id'),
                                       nullable=True)

    loudness_before = db.relationship(Lautstaerke, foreign_keys=[loudness_before_id])
    loudness_after = db.relationship(Lautstaerke, foreign_keys=[loudness_after_id])
    dynamic_trend_before = db.relationship(LautstaerkeEinbettung,
                                           foreign_keys=[dynamic_trend_before_id])
    dynamic_trend_after = db.relationship(LautstaerkeEinbettung,
                                          foreign_keys=[dynamic_trend_after_id])


class DynamicMarking(db.Model, GetByID):
    id = db.Column(db.Integer, primary_key=True)
    dynamic_id = db.Column(db.Integer, db.ForeignKey('dynamic.id'))
    lautstaerke_id = db.Column(db.Integer, db.ForeignKey('lautstaerke.id'))
    lautstaerke_zusatz_id = db.Column(db.Integer, db.ForeignKey('lautstaerke_zusatz.id'), nullable=True)

    dynamic = db.relationship(Dynamic, backref=db.backref('_dynamic_markings', lazy='joined'))
    lautstaerke = db.relationship('Lautstaerke')
    lautstaerke_zusatz = db.relationship('LautstaerkeZusatz')

    def __init__(self, dynamic, lautstaerke, lautstaerke_zusatz=None, **kwargs):
        self.dynamic = dynamic
        self.update(lautstaerke, lautstaerke_zusatz)

    def update(self, lautstaerke, lautstaerke_zusatz=None):
        self.lautstaerke = Lautstaerke.get_by_id_or_dict(lautstaerke)
        self.lautstaerke_zusatz = LautstaerkeZusatz.get_by_id_or_dict(lautstaerke_zusatz)


class LautstaerkeEntwicklungToDynamic(db.Model):
    dynamic_id = db.Column(db.Integer, db.ForeignKey('dynamic.id'), primary_key=True)
    lautstaerke_entwicklung_id = db.Column(db.Integer, db.ForeignKey('lautstaerke_entwicklung.id'), primary_key=True)

    dynamic = db.relationship(Dynamic, backref=db.backref('_dynamic_changes', lazy='joined'))
    lautstaerke_entwicklung = db.relationship('LautstaerkeEntwicklung')

    def __init__(self, dynamic, lautstaerke_entwicklung, **kwargs):
        self.dynamic = dynamic
        self.lautstaerke_entwicklung = lautstaerke_entwicklung
