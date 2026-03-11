from sqlalchemy.orm import relationship

from ... import db
from .helper_classes import ListTaxonomy, TreeTaxonomy

__all__ = ["MusikalischeFunktion", "Verzierung", "VoiceToVoiceRelation"]


class MusikalischeFunktion(db.Model, TreeTaxonomy):
    """DB Model for doc."""

    __tablename__ = "musikalische_funktion"

    display_name = "Musikalische Funktion"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(
        db.Integer, db.ForeignKey(f"{__tablename__}.id", ondelete="CASCADE")
    )
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)

    parent = relationship(
        lambda: MusikalischeFunktion,
        remote_side=[id],
        lazy="select",
        join_depth=1,
        back_populates="children",
    )
    children = relationship(
        lambda: MusikalischeFunktion,
        passive_deletes="all",
        lazy="selectin",
        join_depth=8,
        back_populates="parent",
    )


class Verzierung(db.Model, TreeTaxonomy):
    """DB Model for doc."""

    __tablename__ = "verzierung"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("verzierung.id", ondelete="CASCADE"))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)

    parent = relationship(
        lambda: Verzierung,
        remote_side=[id],
        lazy="select",
        join_depth=1,
        back_populates="children",
    )
    children = relationship(
        lambda: Verzierung,
        passive_deletes="all",
        lazy="selectin",
        join_depth=8,
        back_populates="parent",
    )


class VoiceToVoiceRelation(db.Model, ListTaxonomy):
    """DB Model for choices."""

    __tablename__ = "voice_to_voice_relation"

    display_name = "Stimmen, Beziehung zueinander"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
