from sqlalchemy.orm import relationship

from ... import db
from .helper_classes import TreeTaxonomy

__all__ = ["Akkord"]


class Akkord(db.Model, TreeTaxonomy):
    """DB Model for chords."""

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("akkord.id", ondelete="CASCADE"))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    mapping = db.Column(db.Text(), nullable=True)

    parent = relationship(
        lambda: Akkord,
        remote_side=[id],
        lazy="select",
        join_depth=1,
        back_populates="children",
    )
    children = relationship(
        lambda: Akkord,
        passive_deletes="all",
        lazy="select",
        join_depth=8,
        back_populates="parent",
    )
