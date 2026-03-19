from sqlalchemy.orm import relationship

from ... import db
from .helper_classes import ListTaxonomy, TreeTaxonomy

__all__ = ["SpecAnteil", "SpecAuftreten", "SpecInstrument"]


class SpecAnteil(db.Model, ListTaxonomy):
    """DB Model for specification Anteil."""

    __tablename__ = "spezifikation_anteil"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class SpecAuftreten(db.Model, ListTaxonomy):
    """DB Model for specification Auftreten."""

    __tablename__ = "spezifikation_auftreten"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class SpecInstrument(db.Model, TreeTaxonomy):
    """DB Model for spec instruments."""

    __tablename__ = "spezifikation_instrument"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("spezifikation_instrument.id", ondelete="CASCADE")
    )
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)

    parent = relationship(
        lambda: SpecInstrument,
        remote_side=[id],
        lazy="select",
        join_depth=1,
        back_populates="children",
    )
    children = relationship(
        lambda: SpecInstrument,
        passive_deletes="all",
        lazy="select",
        join_depth=8,
        back_populates="parent",
    )
