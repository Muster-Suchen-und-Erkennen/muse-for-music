from sqlalchemy.orm import relationship

from ... import db
from .helper_classes import ListTaxonomy, TreeTaxonomy

__all__ = [
    "Instrument",
    "InstrumentierungEinbettungQualitaet",
    "InstrumentierungEinbettungQuantitaet",
]


class Instrument(db.Model, TreeTaxonomy):
    """DB Model for instruments."""

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("instrument.id", ondelete="CASCADE"))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)

    parent = relationship(
        lambda: Instrument,
        remote_side=[id],
        lazy="select",
        join_depth=1,
        back_populates="children",
    )
    children = relationship(
        lambda: Instrument,
        passive_deletes="all",
        lazy="select",
        join_depth=8,
        back_populates="parent",
    )


class InstrumentierungEinbettungQualitaet(db.Model, ListTaxonomy):
    """DB Model for choices."""

    __tablename__ = "instrumentierung_einbettung_qualitaet"

    display_name = "Instrumentierung, Qualität der Einbettung"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class InstrumentierungEinbettungQuantitaet(db.Model, ListTaxonomy):
    """DB Model for choices."""

    __tablename__ = "instrumentierung_einbettung_quantitaet"

    display_name = "Instrumentierung, Quantität der Einbettung"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
