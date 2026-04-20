from sqlalchemy.orm import relationship

from ... import db
from .helper_classes import ListTaxonomy, TreeTaxonomy

__all__ = [
    "Lautstaerke",
    "LautstaerkeZusatz",
    "LautstaerkeEntwicklung",
    "LautstaerkeEinbettung",
]


class Lautstaerke(db.Model, ListTaxonomy):
    """DB Model for choices."""

    display_name = "Lautstärke"
    specification = "aai"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class LautstaerkeZusatz(db.Model, ListTaxonomy):
    """DB Model for choices."""

    __tablename__ = "lautstaerke_zusatz"

    display_name = "Lautstärke, Zusatz"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class LautstaerkeEntwicklung(db.Model, TreeTaxonomy):
    """DB Model for dynamic evolution."""

    __tablename__ = "lautstaerke_entwicklung"

    display_name = "Lautstärke-Entwicklung"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("lautstaerke_entwicklung.id", ondelete="CASCADE")
    )
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)

    parent = relationship(
        lambda: LautstaerkeEntwicklung,
        remote_side=[id],
        lazy="select",
        join_depth=1,
        back_populates="children",
    )
    children = relationship(
        lambda: LautstaerkeEntwicklung,
        passive_deletes="all",
        lazy="select",
        join_depth=8,
        back_populates="parent",
    )


class LautstaerkeEinbettung(db.Model, ListTaxonomy):
    """DB Model for choices."""

    __tablename__ = "lautstaerke_einbettung"

    display_name = "Lautstärke-Einbettung"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
