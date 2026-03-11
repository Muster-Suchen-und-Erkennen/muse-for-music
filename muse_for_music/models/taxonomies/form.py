from sqlalchemy.orm import relationship

from ... import db
from .helper_classes import ListTaxonomy, TreeTaxonomy

__all__ = ["FormaleFunktion", "Formschema"]


class FormaleFunktion(db.Model, TreeTaxonomy):
    """DB Model for formal function."""

    __tablename__ = "formale_funktion"

    display_name = "Formale Funktion"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("formale_funktion.id", ondelete="CASCADE")
    )
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)

    parent = relationship(
        lambda: FormaleFunktion,
        remote_side=[id],
        lazy="select",
        join_depth=1,
        back_populates="children",
    )
    children = relationship(
        lambda: FormaleFunktion,
        passive_deletes="all",
        lazy="selectin",
        join_depth=8,
        back_populates="parent",
    )


class Formschema(db.Model, ListTaxonomy):
    """DB Model for choices."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
