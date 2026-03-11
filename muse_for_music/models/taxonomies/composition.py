from sqlalchemy.orm import relationship

from ... import db
from .helper_classes import TreeTaxonomy

__all__ = ["Verarbeitungstechnik", "MusikalischeWendung"]


class Verarbeitungstechnik(db.Model, TreeTaxonomy):
    """DB Model for verarbeitungstechniken."""

    __tablename__ = "verarbeitungstechnik"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("verarbeitungstechnik.id", ondelete="CASCADE")
    )
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)

    parent = relationship(
        lambda: Verarbeitungstechnik,
        remote_side=[id],
        lazy="select",
        join_depth=1,
        back_populates="children",
    )
    children = relationship(
        lambda: Verarbeitungstechnik,
        passive_deletes="all",
        lazy="selectin",
        join_depth=8,
        back_populates="parent",
    )


class MusikalischeWendung(db.Model, TreeTaxonomy):
    """DB Model for doc."""

    __tablename__ = "musikalische_wendung"

    display_name = "Musikalische Wendung"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("musikalische_wendung.id", ondelete="CASCADE")
    )
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)

    parent = relationship(
        lambda: MusikalischeWendung,
        remote_side=[id],
        lazy="select",
        join_depth=1,
        back_populates="children",
    )
    children = relationship(
        lambda: MusikalischeWendung,
        passive_deletes="all",
        lazy="selectin",
        join_depth=8,
        back_populates="parent",
    )
