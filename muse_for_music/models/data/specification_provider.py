from typing import Sequence, Union

from sqlalchemy.orm import Mapped, MappedColumn

from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin, UpdateListMixin
from ..taxonomies import SpecAnteil, SpecAuftreten, SpecInstrument

_ModelMeta = type(db.Model)


class SpecificationProviderMixin:
    def __init_subclass__(cls) -> None:

        tablename = cls.__tablename__
        unique_prefix = tablename.title().replace("_", "")

        # Columns for Specification (must be created per-subclass)
        spec_parent_id = db.Column(db.Integer, db.ForeignKey(tablename + ".id"))

        Specification = _ModelMeta(
            f"{unique_prefix}Specification",
            (db.Model, GetByID, UpdateListMixin, UpdateableModelMixin),
            {
                "__module__": __name__,
                "__qualname__": f"{unique_prefix}Specification",
                "_normal_attributes": (
                    ("share", SpecAnteil),
                    ("occurence", SpecAuftreten),
                    ("path", str),
                ),
                "_list_attributes": ("instrumentation",),
                "__tablename__": tablename + "_specification",
                "id": db.Column(db.Integer, primary_key=True),
                "path": db.Column(db.Text),
                "parent_id": spec_parent_id,
                "share_id": db.Column(
                    db.Integer, db.ForeignKey(SpecAnteil.id), nullable=True
                ),
                "occurence_id": db.Column(
                    db.Integer, db.ForeignKey(SpecAuftreten.id), nullable=True
                ),
                "share": db.relationship(SpecAnteil, lazy="selectin"),
                "occurence": db.relationship(SpecAuftreten, lazy="selectin"),
                "parent": db.relationship(
                    cls,
                    backref=db.backref(
                        "_specifications",
                        lazy="selectin",
                        single_parent=True,
                        cascade="all, delete-orphan",
                    ),
                    foreign_keys=[spec_parent_id],
                ),
            },
        )

        def spec_init(self, parent, **kwargs) -> None:
            db.Model.__init__(self)
            self.parent = parent
            if kwargs:
                self.update(kwargs)

        Specification.__init__ = spec_init

        # SpecInstrumentToSpecification association table
        SpecInstrumentToSpecification = _ModelMeta(
            f"{unique_prefix}SpecInstrumentToSpecification",
            (db.Model,),
            {
                "__module__": __name__,
                "__qualname__": f"{unique_prefix}SpecInstrumentToSpecification",
                "__tablename__": tablename + "_spec_instrument_to_specification",
                "specifications_id": db.Column(
                    db.Integer,
                    db.ForeignKey(Specification.__tablename__ + ".id"),
                    primary_key=True,
                ),
                "spezifikation_instrument_id": db.Column(
                    db.Integer,
                    db.ForeignKey("spezifikation_instrument.id"),
                    primary_key=True,
                ),
                "specifications": db.relationship(
                    Specification,
                    backref=db.backref(
                        "_spezifikation_instrument",
                        lazy="selectin",
                        single_parent=True,
                        cascade="all, delete-orphan",
                    ),
                ),
                "spezifikation_instrument": db.relationship("SpecInstrument"),
            },
        )

        def assoc_init(self, specifications, spezifikation_instrument, **kwargs):
            self.specifications = specifications
            self.spezifikation_instrument = spezifikation_instrument

        SpecInstrumentToSpecification.__init__ = assoc_init

        # Add instrumentation property to Specification (needs SpecInstrumentToSpecification)
        def get_instrumentation(self):
            return [
                mapping.spezifikation_instrument
                for mapping in self._spezifikation_instrument
            ]

        def set_instrumentation(
            self, spezifikation_instrument_list: Union[Sequence[int], Sequence[dict]]
        ):
            old_items = {
                mapping.spezifikation_instrument.id: mapping
                for mapping in self._spezifikation_instrument
            }
            self.update_list(
                spezifikation_instrument_list,
                old_items,
                SpecInstrumentToSpecification,
                SpecInstrument,
                "spezifikation_instrument",
            )

        Specification.instrumentation = property(get_instrumentation, set_instrumentation)

        cls._Specification = Specification

    @property
    def specifications(self):
        return self._specifications

    @specifications.setter
    def specifications(self, specifications_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.id: mapping for mapping in self._specifications}
        self.update_list(specifications_list, old_items, self._Specification)
