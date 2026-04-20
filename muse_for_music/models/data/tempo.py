from typing import Sequence, Union

from sqlalchemy.orm import Mapped, MappedColumn, relationship

from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin, UpdateListMixin
from ..taxonomies import Tempo, TempoEinbettung, TempoEntwicklung


class TempoContext(db.Model, GetByID, UpdateableModelMixin):

    _normal_attributes = (
        ("tempo_trend_before", TempoEntwicklung),
        ("tempo_context_before", TempoEinbettung),
        ("tempo_trend_after", TempoEntwicklung),
        ("tempo_context_after", TempoEinbettung),
    )

    __tablename__ = "tempo_context"
    id = db.Column(db.Integer, primary_key=True)

    tempo_context_before_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(TempoEinbettung.id), nullable=True
    )
    tempo_context_after_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(TempoEinbettung.id), nullable=True
    )
    tempo_trend_before_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(TempoEntwicklung.id), nullable=True
    )
    tempo_trend_after_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(TempoEntwicklung.id), nullable=True
    )

    tempo_context_before: Mapped[TempoEinbettung] = relationship(
        TempoEinbettung, lazy="selectin", foreign_keys=[tempo_context_before_id]
    )
    tempo_context_after: Mapped[TempoEinbettung] = relationship(
        TempoEinbettung, lazy="selectin", foreign_keys=[tempo_context_after_id]
    )
    tempo_trend_before: Mapped[TempoEntwicklung] = relationship(
        TempoEntwicklung, lazy="selectin", foreign_keys=[tempo_trend_before_id]
    )
    tempo_trend_after: Mapped[TempoEntwicklung] = relationship(
        TempoEntwicklung, lazy="selectin", foreign_keys=[tempo_trend_after_id]
    )


class TempoGroup(db.Model, GetByID, UpdateableModelMixin, UpdateListMixin):

    _list_attributes = ("tempo_markings", "tempo_changes")

    __tablename__ = "tempo_group"
    id = db.Column(db.Integer, primary_key=True)

    # backrefs
    _tempo_markings: Mapped[list["TempoToTempoGroup"]] = relationship(
        lambda: TempoToTempoGroup,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="tempo_group",
    )
    _tempo_changes: Mapped[list["TempoEntwicklungToTempoGroup"]] = relationship(
        lambda: TempoEntwicklungToTempoGroup,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="tempo_group",
    )

    @property
    def tempo_markings(self):
        return [mapping.tempo for mapping in self._tempo_markings]

    @tempo_markings.setter
    def tempo_markings(self, tempo_markings_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.tempo.id: mapping for mapping in self._tempo_markings}
        self.update_list(
            tempo_markings_list, old_items, TempoToTempoGroup, Tempo, "tempo"
        )

    @property
    def tempo_changes(self):
        return [mapping.tempo_entwicklung for mapping in self._tempo_changes]

    @tempo_changes.setter
    def tempo_changes(self, tempo_changes_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {
            mapping.tempo_entwicklung.id: mapping for mapping in self._tempo_changes
        }
        self.update_list(
            tempo_changes_list,
            old_items,
            TempoEntwicklungToTempoGroup,
            TempoEntwicklung,
            "tempo_entwicklung",
        )


class TempoToTempoGroup(db.Model):
    tempo_group_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(TempoGroup.id), primary_key=True
    )
    tempo_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Tempo.id), primary_key=True
    )

    tempo_group: Mapped[TempoGroup] = relationship(
        TempoGroup, back_populates="_tempo_markings"
    )
    tempo: Mapped[Tempo] = relationship(Tempo, lazy="selectin")

    def __init__(self, tempo_group, tempo, **kwargs):
        self.tempo_group = tempo_group
        self.tempo = tempo


class TempoEntwicklungToTempoGroup(db.Model):
    tempo_group_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(TempoGroup.id), primary_key=True
    )
    tempo_entwicklung_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(TempoEntwicklung.id), primary_key=True
    )

    tempo_group: Mapped[TempoGroup] = relationship(
        TempoGroup, back_populates="_tempo_changes"
    )
    tempo_entwicklung: Mapped[TempoEntwicklung] = relationship(
        TempoEntwicklung, lazy="selectin"
    )

    def __init__(self, tempo_group, tempo_entwicklung, **kwargs):
        self.tempo_group = tempo_group
        self.tempo_entwicklung = tempo_entwicklung
