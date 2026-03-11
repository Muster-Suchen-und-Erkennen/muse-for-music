from sqlalchemy.orm import relationship

from ... import db
from .helper_classes import ListTaxonomy, TreeTaxonomy

__all__ = ["AmbitusEntwicklung", "AmbitusEinbettung"]


class AmbitusEntwicklung(db.Model, TreeTaxonomy):
    """DB Model for ambitus change."""

    __tablename__ = "ambitus_entwicklung"

    display_name = "Ambitus-Entwicklung"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("ambitus_entwicklung.id", ondelete="CASCADE")
    )
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)

    parent = relationship(
        lambda: AmbitusEntwicklung,
        remote_side=[id],
        lazy="select",
        join_depth=1,
        back_populates="children",
    )
    children = relationship(
        lambda: AmbitusEntwicklung,
        passive_deletes="all",
        lazy="selectin",
        join_depth=8,
        back_populates="parent",
    )


class AmbitusEinbettung(db.Model, ListTaxonomy):
    """DB Model for choices."""

    __tablename__ = "ambitus_einbettung"

    display_name = "Ambitus-Einbettung"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
