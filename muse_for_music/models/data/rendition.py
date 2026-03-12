from typing import Sequence, Union

from sqlalchemy.orm import Mapped, MappedColumn, relationship

from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin, UpdateListMixin
from ..taxonomies import Artikulation, Ausdruck, Spielanweisung


class Rendition(db.Model, GetByID, UpdateableModelMixin, UpdateListMixin):

    _list_attributes = ("mood_markings", "articulation_markings", "technic_markings")

    __tablename__ = "rendition"
    id = db.Column(db.Integer, primary_key=True)

    # backrefs
    _mood_markings: Mapped[list["AusdruckToRendition"]] = relationship(
        lambda: AusdruckToRendition,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="rendition",
    )
    _articulation_markings: Mapped[list["ArtikulationToRendition"]] = relationship(
        lambda: ArtikulationToRendition,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="rendition",
    )
    _technic_markings: Mapped[list["SpielanweisungToRendition"]] = relationship(
        lambda: SpielanweisungToRendition,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="rendition",
    )

    @property
    def mood_markings(self):
        return [mapping.ausdruck for mapping in self._mood_markings]

    @mood_markings.setter
    def mood_markings(self, mood_markings_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.ausdruck.id: mapping for mapping in self._mood_markings}
        self.update_list(
            mood_markings_list, old_items, AusdruckToRendition, Ausdruck, "ausdruck"
        )

    @property
    def articulation_markings(self):
        return [mapping.artikulation for mapping in self._articulation_markings]

    @articulation_markings.setter
    def articulation_markings(
        self, articulation_markings_list: Union[Sequence[int], Sequence[dict]]
    ):
        old_items = {
            mapping.artikulation.id: mapping for mapping in self._articulation_markings
        }
        self.update_list(
            articulation_markings_list,
            old_items,
            ArtikulationToRendition,
            Artikulation,
            "artikulation",
        )

    @property
    def technic_markings(self):
        return [mapping.spielanweisung for mapping in self._technic_markings]

    @technic_markings.setter
    def technic_markings(
        self, technic_markings_list: Union[Sequence[int], Sequence[dict]]
    ):
        old_items = {
            mapping.spielanweisung.id: mapping for mapping in self._technic_markings
        }
        self.update_list(
            technic_markings_list,
            old_items,
            SpielanweisungToRendition,
            Spielanweisung,
            "spielanweisung",
        )


class AusdruckToRendition(db.Model):
    rendition_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Rendition.id), primary_key=True
    )
    ausdruck_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Ausdruck.id), primary_key=True
    )

    rendition: Mapped[Rendition] = relationship(
        Rendition, back_populates="_mood_markings"
    )
    ausdruck: Mapped[Ausdruck] = relationship(Ausdruck)

    def __init__(self, rendition, ausdruck, **kwargs):
        self.rendition = rendition
        self.ausdruck = ausdruck


class ArtikulationToRendition(db.Model):
    rendition_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Rendition.id), primary_key=True
    )
    artikulation_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Artikulation.id), primary_key=True
    )

    rendition: Mapped[Rendition] = relationship(
        Rendition, back_populates="_articulation_markings"
    )
    artikulation: Mapped[Artikulation] = relationship(Artikulation)

    def __init__(self, rendition, artikulation, **kwargs):
        self.rendition = rendition
        self.artikulation = artikulation


class SpielanweisungToRendition(db.Model):
    rendition_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Rendition.id), primary_key=True
    )
    spielanweisung_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Spielanweisung.id), primary_key=True
    )

    rendition: Mapped[Rendition] = relationship(
        Rendition, back_populates="_technic_markings"
    )
    spielanweisung: Mapped[Spielanweisung] = relationship(Spielanweisung)

    def __init__(self, rendition, spielanweisung, **kwargs):
        self.rendition = rendition
        self.spielanweisung = spielanweisung
