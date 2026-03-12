from typing import Sequence, Union, ClassVar, Protocol, Generic, TypeVar

from sqlalchemy.orm import Mapped, MappedColumn, relationship
from flask_sqlalchemy.model import Model
from typing_extensions import Self

from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin, UpdateListMixin
from ..taxonomies import SpecAnteil, SpecAuftreten, SpecInstrument

T = TypeVar("T")


class SpecificationProto(Generic[T], Protocol):
    _normal_attributes: tuple[tuple[str, type], ...]
    _list_attributes: tuple[str, ...]

    # base columns
    id: MappedColumn[int]
    path: MappedColumn[str]
    parent_id: MappedColumn[int]
    share_id: MappedColumn[int | None]
    occurence_id: MappedColumn[int | None]

    # relationships
    share: Mapped[SpecAnteil | None]
    occurence: Mapped[SpecAuftreten | None]
    parent: Mapped[T | None]
    _spezifikation_instrument: Mapped[list["SpecInstrumentToSpecificationProto[T]"]]
    instrumentation: list[SpecInstrument]

    def __init__(self, parent: T, **kwargs) -> None: ...  # noqa: E704


class SpecInstrumentToSpecificationProto(Generic[T], Protocol):
    specifications_id: MappedColumn[int]
    spezifikation_instrument_id: MappedColumn[int]
    # relations
    specifications: Mapped[SpecificationProto[T]]
    spezifikation_instrument: Mapped[SpecInstrument]

    def __init__(  # noqa: E704
        self,
        specifications: SpecificationProto[T],
        spezifikation_instrument: SpecInstrument,
        **kwargs,
    ) -> None: ...


class SpecificationProviderMixin:

    _Specification: ClassVar[type[SpecificationProto[Self]]]
    _specifications: Mapped[list[SpecificationProto[Self]]]

    def __init_subclass__(cls) -> None:

        assert issubclass(cls, Model)
        assert issubclass(cls, GetByID)
        assert issubclass(cls, UpdateListMixin)
        assert hasattr(cls, "__tablename__")

        tablename: str = cls.__tablename__  # type: ignore

        # spec methods:
        def specification__init__(self, parent, **kwargs) -> None:
            super(spec_class, self).__init__()
            self.parent = parent
            if kwargs:
                self.update(kwargs)

        specification__init__.__name__ = "__init__"

        def specification_get_instrumentation(self):
            return [
                mapping.spezifikation_instrument
                for mapping in self._spezifikation_instrument
            ]

        def specification_set_instrumentation(
            self, spezifikation_instrument_list: Union[Sequence[int], Sequence[dict]]
        ):
            old_items = {
                mapping.spezifikation_instrument.id: mapping
                for mapping in self._spezifikation_instrument
            }
            self.update_list(
                spezifikation_instrument_list,
                old_items,
                spec_instrument_to_spec_class,
                SpecInstrument,
                "spezifikation_instrument",
            )

        spec_class: type[SpecificationProto[Self]] = type(
            f"{cls.__name__}Specification",
            (db.Model, GetByID, UpdateListMixin, UpdateableModelMixin),
            {
                "__tablename__": f"{tablename}_specification",
                # metadata for updatable classes
                "_normal_attributes": (
                    ("share", SpecAnteil),
                    ("occurence", SpecAuftreten),
                    ("path", str),
                ),
                "_list_attributes": ("instrumentation",),
                # base columns
                "id": db.Column(db.Integer, primary_key=True),
                "path": db.Column(db.Text),
                "parent_id": db.Column(db.Integer, db.ForeignKey(f"{tablename}.id")),
                "share_id": db.Column(
                    db.Integer, db.ForeignKey(SpecAnteil.id), nullable=True
                ),
                "occurence_id": db.Column(
                    db.Integer, db.ForeignKey(SpecAuftreten.id), nullable=True
                ),
                # relationships
                "share": relationship(SpecAnteil, lazy="selectin"),
                "occurence": relationship(SpecAuftreten, lazy="selectin"),
                "parent": relationship(cls, back_populates="_specifications"),
                "_spezifikation_instrument": relationship(
                    lambda: spec_instrument_to_spec_class,
                    lazy="selectin",
                    single_parent=True,
                    cascade="all, delete-orphan",
                    back_populates="specifications",
                ),
                "instrumentation": property(
                    specification_get_instrumentation, specification_set_instrumentation
                ),
                # __init__
                "__init__": specification__init__,  # type: ignore
            },
        )

        # spec intrument to spec methods:
        def spec_instrument_to_spec__init__(
            self,
            specifications: SpecificationProto[Self],
            spezifikation_instrument: SpecInstrument,
            **kwargs,
        ):
            self.specifications = specifications
            self.spezifikation_instrument = spezifikation_instrument

        spec_instrument_to_spec__init__.__name__ = "__init__"

        spec_instrument_to_spec_class: type[SpecInstrumentToSpecificationProto[Self]] = (
            type(
                f"SpecInstrumentTo{cls.__name__}Specification",
                (db.Model,),
                {
                    "__tablename__": f"{tablename}_spec_instrument_to_specification",
                    # columns
                    "specifications_id": db.Column(
                        db.Integer,
                        db.ForeignKey(spec_class.id),
                        primary_key=True,
                    ),
                    "spezifikation_instrument_id": db.Column(
                        db.Integer, db.ForeignKey(SpecInstrument.id), primary_key=True
                    ),
                    # relations
                    "specifications": relationship(
                        spec_class, back_populates="_spezifikation_instrument"
                    ),
                    "spezifikation_instrument": relationship(SpecInstrument),
                    # __init__
                    "__init__": spec_instrument_to_spec__init__,  # type: ignore
                },
            )
        )

        cls._Specification = spec_class  # type: ignore assignment
        cls._specifications = relationship(
            spec_class,
            lazy="selectin",
            single_parent=True,
            cascade="all, delete-orphan",
            back_populates="parent",
        )

    @property
    def specifications(self):
        return self._specifications

    @specifications.setter
    def specifications(self, specifications_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.id: mapping for mapping in self._specifications}
        assert isinstance(self, UpdateListMixin)
        self.update_list(
            specifications_list,
            old_items,  # type: ignore
            self._Specification,  # type: ignore
        )
