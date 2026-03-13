from sqlalchemy.orm import relationship

from ... import db
from .helper_classes import TreeTaxonomy

__all__ = ["Zitat", "Programmgegenstand", "Tonmalerei"]


class Zitat(db.Model, TreeTaxonomy):
    """DB Model for citation."""

    __tablename__ = "zitat"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("zitat.id", ondelete="CASCADE"))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)

    parent = relationship(
        lambda: Zitat,
        remote_side=[id],
        lazy="select",
        join_depth=1,
        back_populates="children",
    )
    children = relationship(
        lambda: Zitat,
        passive_deletes="all",
        lazy="selectin",
        join_depth=8,
        back_populates="parent",
    )


class Programmgegenstand(db.Model, TreeTaxonomy):
    """DB Model for doc."""

    __tablename__ = "programmgegenstand"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("programmgegenstand.id", ondelete="CASCADE")
    )
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)

    parent = relationship(
        lambda: Programmgegenstand,
        remote_side=[id],
        lazy="select",
        join_depth=1,
        back_populates="children",
    )
    children = relationship(
        lambda: Programmgegenstand,
        passive_deletes="all",
        lazy="selectin",
        join_depth=8,
        back_populates="parent",
    )


class Tonmalerei(db.Model, TreeTaxonomy):
    """DB Model for doc."""

    __tablename__ = "tonmalerei"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("tonmalerei.id", ondelete="CASCADE"))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)

    parent = relationship(
        lambda: Tonmalerei,
        remote_side=[id],
        lazy="select",
        join_depth=1,
        back_populates="children",
    )
    children = relationship(
        lambda: Tonmalerei,
        passive_deletes="all",
        lazy="selectin",
        join_depth=8,  # FIXME test!!!
        back_populates="parent",
    )
