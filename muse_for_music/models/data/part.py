from typing import Sequence, Union

from sqlalchemy.orm import Mapped, MappedColumn, relationship

from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin, UpdateListMixin
from ..taxonomies import AuftretenSatz, FormaleFunktion
from .dramaturgic_context import DramaturgicContext
from .dynamic import DynamicContext
from .instrumentation import InstrumentationContext
from .measure import Measure
from .opus import Opus
from .specification_provider import SpecificationProviderMixin
from .tempo import TempoContext


class Part(
    db.Model, GetByID, UpdateableModelMixin, UpdateListMixin, SpecificationProviderMixin
):

    _normal_attributes = (
        ("name", str),
        ("measure_start", Measure),
        ("measure_end", Measure),
        ("length", int),
        ("omissions", str),
        ("movement", int),
        ("dramaturgic_context", DramaturgicContext),
        ("tempo_context", TempoContext),
        ("dynamic_context", DynamicContext),
        ("instrumentation_context", InstrumentationContext),
    )

    _list_attributes = ("formal_functions", "occurence_in_movement", "specifications")

    __tablename__ = "part"

    id = db.Column(db.Integer, primary_key=True)
    opus_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Opus.id), nullable=False
    )
    name: MappedColumn[str | None] = db.Column(db.String(191), nullable=True)
    movement: MappedColumn[int] = db.Column(db.Integer, nullable=False)
    measure_start_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Measure.id), nullable=False
    )
    measure_end_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Measure.id), nullable=False
    )
    length: MappedColumn[int] = db.Column(db.Integer, nullable=False)
    # occurence_in_movement_id = db.Column(db.Integer, db.ForeignKey('auftreten_satz.id'), nullable=True)
    instrumentation_context_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(InstrumentationContext.id), nullable=True
    )
    dynamic_context_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(DynamicContext.id), nullable=True
    )
    tempo_context_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(TempoContext.id), nullable=True
    )
    dramaturgic_context_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(DramaturgicContext.id), nullable=True
    )

    opus: Mapped[Opus] = relationship(Opus, lazy="select", back_populates="parts")
    measure_start: Mapped[Measure] = relationship(
        Measure,
        foreign_keys=[measure_start_id],
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
    )
    measure_end: Mapped[Measure] = relationship(
        Measure,
        foreign_keys=[measure_end_id],
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
    )
    omissions = db.Column(db.Text, nullable=True)
    # occurence_in_movement = relationship(AuftretenSatz, lazy='selectin')
    instrumentation_context: Mapped[InstrumentationContext] = relationship(
        InstrumentationContext, single_parent=True, cascade="all, delete-orphan"
    )
    dynamic_context: Mapped[DynamicContext] = relationship(
        DynamicContext, single_parent=True, cascade="all, delete-orphan"
    )
    tempo_context: Mapped[TempoContext] = relationship(
        TempoContext, single_parent=True, cascade="all, delete-orphan"
    )
    dramaturgic_context: Mapped[DramaturgicContext] = relationship(
        DramaturgicContext, single_parent=True, cascade="all, delete-orphan"
    )

    # cross-file backref: SubPart.part uses back_populates="subparts"
    subparts: Mapped[list["SubPart"]] = relationship(
        "SubPart",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="part",
    )

    # backrefs for association tables
    _formal_functions: Mapped[list["FormaleFunktionToPart"]] = relationship(
        lambda: FormaleFunktionToPart,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="part",
    )
    _occurence_in_movement: Mapped[list["AuftretenSatzToPart"]] = relationship(
        lambda: AuftretenSatzToPart,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="part",
    )

    _eager_load = [
        "dramaturgic_context",
        "tempo_context",
        "dynamic_context",
        "instrumentation_context",
        "subparts",
    ]

    def __init__(
        self,
        opus_id: int,
        measure_start: dict,
        measure_end: dict,
        length: int = 1,
        movement: int = 1,
        name: str = "",
        omissions: str = "",
        **kwargs,
    ):
        self.opus = Opus.get_by_id(opus_id)
        self.name = name
        self.movement = movement
        self.measure_start = Measure(**measure_start)
        self.measure_end = Measure(**measure_end)
        db.session.add(self.measure_start)
        db.session.add(self.measure_end)
        self.length = length
        self.omissions = omissions

        self.instrumentation_context = InstrumentationContext()
        self.dynamic_context = DynamicContext()
        self.tempo_context = TempoContext()
        self.dramaturgic_context = DramaturgicContext()
        db.session.add(self.instrumentation_context)
        db.session.add(self.dynamic_context)
        db.session.add(self.tempo_context)
        db.session.add(self.dramaturgic_context)

        from .history import History, MethodEnum
        from .subpart import SubPart

        subpart = SubPart(self)
        db.session.add(subpart)

        hist = History(MethodEnum.create, subpart)
        db.session.add(hist)

    @property
    def formal_functions(self):
        return [mapping.formale_funktion for mapping in self._formal_functions]

    @formal_functions.setter
    def formal_functions(
        self, formal_functions_list: Union[Sequence[int], Sequence[dict]]
    ):
        old_items = {
            mapping.formale_funktion.id: mapping for mapping in self._formal_functions
        }
        self.update_list(
            formal_functions_list,
            old_items,
            FormaleFunktionToPart,
            FormaleFunktion,
            "formale_funktion",
        )

    @property
    def occurence_in_movement(self):
        return [mapping.auftreten_satz for mapping in self._occurence_in_movement]

    @occurence_in_movement.setter
    def occurence_in_movement(
        self, occurence_in_movement_list: Union[Sequence[int], Sequence[dict]]
    ):
        old_items = {
            mapping.auftreten_satz.id: mapping for mapping in self._occurence_in_movement
        }
        self.update_list(
            occurence_in_movement_list,
            old_items,
            AuftretenSatzToPart,
            AuftretenSatz,
            "auftreten_satz",
        )


class FormaleFunktionToPart(db.Model):
    part_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Part.id), primary_key=True
    )
    formale_funktion_id: MappedColumn[int] = db.Column(
        db.Integer,
        db.ForeignKey(
            FormaleFunktion.id, name="fk_formale_funktion_to_part_formale_funktion_id"
        ),
        primary_key=True,
    )

    part: Mapped[Part] = relationship(Part, back_populates="_formal_functions")
    formale_funktion: Mapped[FormaleFunktion] = relationship(FormaleFunktion)

    def __init__(self, part, formale_funktion, **kwargs):
        self.part = part
        self.formale_funktion = formale_funktion


class AuftretenSatzToPart(db.Model):
    part_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Part.id), primary_key=True
    )
    auftreten_satz_id: MappedColumn[int] = db.Column(
        db.Integer,
        db.ForeignKey(
            AuftretenSatz.id, name="fk_auftreten_satz_to_part_auftreten_satz_id"
        ),
        primary_key=True,
    )

    part: Mapped[Part] = relationship(Part, back_populates="_occurence_in_movement")
    auftreten_satz: Mapped[AuftretenSatz] = relationship(AuftretenSatz)

    def __init__(self, part, auftreten_satz, **kwargs):
        self.part = part
        self.auftreten_satz = auftreten_satz
