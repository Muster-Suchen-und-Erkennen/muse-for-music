from typing import Sequence, Union

from sqlalchemy.orm import Mapped, MappedColumn, relationship

from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin, UpdateListMixin
from ..taxonomies import (
    Lautstaerke,
    LautstaerkeEinbettung,
    LautstaerkeEntwicklung,
    LautstaerkeZusatz,
)


class Dynamic(db.Model, GetByID, UpdateableModelMixin, UpdateListMixin):

    _list_attributes = ("dynamic_markings", "dynamic_changes")

    __tablename__ = "dynamic"
    id = db.Column(db.Integer, primary_key=True)

    # backrefs
    _dynamic_markings: Mapped[list["DynamicMarking"]] = relationship(
        lambda: DynamicMarking,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="dynamic",
    )
    _dynamic_changes: Mapped[list["LautstaerkeEntwicklungToDynamic"]] = relationship(
        lambda: LautstaerkeEntwicklungToDynamic,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="dynamic",
    )

    @property
    def dynamic_changes(self):
        return [mapping.lautstaerke_entwicklung for mapping in self._dynamic_changes]

    @dynamic_changes.setter
    def dynamic_changes(self, dynamic_changes_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {
            mapping.lautstaerke_entwicklung.id: mapping
            for mapping in self._dynamic_changes
        }
        self.update_list(
            dynamic_changes_list,
            old_items,
            LautstaerkeEntwicklungToDynamic,
            LautstaerkeEntwicklung,
            "lautstaerke_entwicklung",
        )

    @property
    def dynamic_markings(self):
        return self._dynamic_markings

    @dynamic_markings.setter
    def dynamic_markings(self, dynamic_markings_list: Sequence[dict]):
        old_items = {mark.id: mark for mark in self._dynamic_markings}
        self.update_list(dynamic_markings_list, old_items, DynamicMarking)


class DynamicContext(db.Model, GetByID, UpdateableModelMixin):
    __tablename__ = "dynamic_context"

    _normal_attributes = (
        ("loudness_before", Lautstaerke),
        ("dynamic_trend_before", LautstaerkeEinbettung),
        ("loudness_after", Lautstaerke),
        ("dynamic_trend_after", LautstaerkeEinbettung),
    )

    id = db.Column(db.Integer, primary_key=True)

    loudness_before_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Lautstaerke.id), nullable=True
    )
    loudness_after_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Lautstaerke.id), nullable=True
    )
    dynamic_trend_before_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(LautstaerkeEinbettung.id), nullable=True
    )
    dynamic_trend_after_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(LautstaerkeEinbettung.id), nullable=True
    )

    loudness_before: Mapped[Lautstaerke] = relationship(
        Lautstaerke, foreign_keys=[loudness_before_id]
    )
    loudness_after: Mapped[Lautstaerke] = relationship(
        Lautstaerke, foreign_keys=[loudness_after_id]
    )
    dynamic_trend_before: Mapped[LautstaerkeEinbettung] = relationship(
        LautstaerkeEinbettung, foreign_keys=[dynamic_trend_before_id]
    )
    dynamic_trend_after: Mapped[LautstaerkeEinbettung] = relationship(
        LautstaerkeEinbettung, foreign_keys=[dynamic_trend_after_id]
    )


class DynamicMarking(db.Model, GetByID, UpdateableModelMixin):

    _normal_attributes = (
        ("lautstaerke_zusatz", LautstaerkeZusatz),
        ("lautstaerke", Lautstaerke),
    )

    id: MappedColumn[int] = db.Column(db.Integer, primary_key=True)
    dynamic_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Dynamic.id)
    )
    lautstaerke_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Lautstaerke.id)
    )
    lautstaerke_zusatz_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(LautstaerkeZusatz.id), nullable=True
    )

    dynamic: Mapped[Dynamic] = relationship(Dynamic, back_populates="_dynamic_markings")
    lautstaerke: Mapped[Lautstaerke] = relationship(Lautstaerke)
    lautstaerke_zusatz: Mapped[LautstaerkeZusatz] = relationship(LautstaerkeZusatz)

    def __init__(self, dynamic, **kwargs):
        self.dynamic = dynamic
        if kwargs:
            self.update(kwargs)


class LautstaerkeEntwicklungToDynamic(db.Model):
    dynamic_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Dynamic.id), primary_key=True
    )
    lautstaerke_entwicklung_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(LautstaerkeEntwicklung.id), primary_key=True
    )

    dynamic: Mapped[Dynamic] = relationship(
        Dynamic, back_populates="_dynamic_changes"
    )
    lautstaerke_entwicklung: Mapped[LautstaerkeEntwicklung] = relationship(
        LautstaerkeEntwicklung
    )

    def __init__(self, dynamic, lautstaerke_entwicklung, **kwargs):
        self.dynamic = dynamic
        self.lautstaerke_entwicklung = lautstaerke_entwicklung
