from typing import Union

from sqlalchemy.orm import Mapped, MappedColumn, relationship

from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin, UpdateListMixin
from ..taxonomies import Anteil, AuftretenWerkausschnitt
from .dynamic import Dynamic
from .harmonics import Harmonics
from .instrumentation import Instrumentation
from .part import Part
from .satz import Satz
from .specification_provider import SpecificationProviderMixin
from .tempo import TempoGroup


class SubPart(
    db.Model, GetByID, UpdateableModelMixin, UpdateListMixin, SpecificationProviderMixin
):

    _normal_attributes = (
        ("label", str),
        ("measures", str),
        ("occurence_in_part", AuftretenWerkausschnitt),
        ("share_of_part", Anteil),
        ("is_tutti", bool),
        ("dynamic", Dynamic),
        ("harmonics", Harmonics),
        ("tempo", TempoGroup),
    )

    _list_attributes = ("instrumentation", "specifications")

    __tablename__ = "sub_part"

    id = db.Column(db.Integer, primary_key=True)
    part_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Part.id), nullable=False
    )
    label: MappedColumn[str] = db.Column(db.String(191), nullable=False, default="A")
    measures: MappedColumn[str | None] = db.Column(db.Text, nullable=True)
    occurence_in_part_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(AuftretenWerkausschnitt.id), nullable=True
    )
    share_of_part_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Anteil.id), nullable=True
    )
    instrumentation_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Instrumentation.id)
    )
    is_tutti: MappedColumn[bool] = db.Column(db.Boolean, default=False)
    dynamic_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Dynamic.id), nullable=True
    )
    harmonics_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Harmonics.id), nullable=True
    )
    tempo_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(TempoGroup.id), nullable=True
    )
    # ambitus_id = db.Column(db.Integer, db.ForeignKey('ambitus_group.id'), nullable=True)

    part: Mapped[Part] = relationship(Part, lazy="select", back_populates="subparts")
    occurence_in_part: Mapped[AuftretenWerkausschnitt] = relationship(
        AuftretenWerkausschnitt, lazy="selectin", single_parent=True
    )
    share_of_part: Mapped[Anteil] = relationship(
        Anteil, lazy="selectin", single_parent=True
    )
    _instrumentation: Mapped[Instrumentation] = relationship(
        Instrumentation,
        lazy="subquery",
        single_parent=True,
        cascade="all, delete-orphan",
    )
    dynamic: Mapped[Dynamic] = relationship(
        Dynamic, single_parent=True, cascade="all, delete-orphan"
    )
    harmonics: Mapped[Harmonics] = relationship(
        Harmonics, single_parent=True, cascade="all, delete-orphan"
    )
    tempo: Mapped[TempoGroup] = relationship(
        TempoGroup, single_parent=True, cascade="all, delete-orphan"
    )
    # ambitus = relationship(AmbitusGroup, single_parent=True, cascade="all, delete-orphan")

    # cross-file backref: Voice.subpart uses back_populates="voices"
    voices: Mapped[list["Voice"]] = relationship(
        lambda: Voice,
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="subpart",
    )

    _eager_load = ["dynamic", "harmonics", "voices"]

    def __init__(self, part_id: Union[int, Part], label: str = "A", **kwargs):
        if isinstance(part_id, Part):
            self.part = part_id
        else:
            found_part = Part.get_by_id(part_id)
            if found_part is None:
                raise KeyError(f"Did not find a part with Part.id=={part_id}.")
            self.part = found_part
        self.label = label

        self.satz = Satz()
        db.session.add(self.satz)

        self._instrumentation = Instrumentation()
        db.session.add(self._instrumentation)

    @property
    def instrumentation(self):
        return self._instrumentation.instruments

    @instrumentation.setter
    def instrumentation(self, data: list):
        self._instrumentation.instruments = data


from .voice import Voice  # noqa
