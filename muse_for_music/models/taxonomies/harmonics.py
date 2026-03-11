from sqlalchemy.orm import relationship

from ... import db
from .helper_classes import ListTaxonomy, TreeTaxonomy

__all__ = [
    "HarmonischeEntwicklung",
    "Tonalitaet",
    "HarmonischeFunktion",
    "HarmonischeStufe",
    "HarmonischeFunktionVerwandschaft",
    "HarmonischePhaenomene",
    "HarmonischeKomplexitaet",
    "HarmonischeDichte",
    "AnzahlMelodietoene",
]


class HarmonischeEntwicklung(db.Model, TreeTaxonomy):
    """DB Model for harmonic modulation."""

    display_name = "Harmonische Entwicklung"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("harmonische_entwicklung.id", ondelete="CASCADE")
    )
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)

    parent = relationship(
        lambda: HarmonischeEntwicklung,
        remote_side=[id],
        lazy="select",
        join_depth=1,
        back_populates="children",
    )
    children = relationship(
        lambda: HarmonischeEntwicklung,
        passive_deletes="all",
        lazy="selectin",
        join_depth=8,
        back_populates="parent",
    )


class Tonalitaet(db.Model, TreeTaxonomy):
    """DB Model for tonality."""

    __tablename__ = "tonalitaet"

    display_name = "Tonalität"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("tonalitaet.id", ondelete="CASCADE"))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)

    parent = relationship(
        lambda: Tonalitaet,
        remote_side=[id],
        lazy="select",
        join_depth=1,
        back_populates="children",
    )
    children = relationship(
        lambda: Tonalitaet,
        passive_deletes="all",
        lazy="selectin",
        join_depth=8,
        back_populates="parent",
    )


class HarmonischeFunktion(db.Model, ListTaxonomy):
    """DB Model for choices."""

    __tablename__ = "harmonische_funktion"

    display_name = "Harmonische Funktion"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class HarmonischeStufe(db.Model, TreeTaxonomy):
    """DB Model for harmonic level."""

    __tablename__ = "harmonische_stufe"

    display_name = "Harmonische Stufe"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("harmonische_stufe.id", ondelete="CASCADE")
    )
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)

    parent = relationship(
        lambda: HarmonischeStufe,
        remote_side=[id],
        lazy="select",
        join_depth=1,
        back_populates="children",
    )
    children = relationship(
        lambda: HarmonischeStufe,
        passive_deletes="all",
        lazy="selectin",
        join_depth=8,
        back_populates="parent",
    )


class HarmonischeFunktionVerwandschaft(db.Model, TreeTaxonomy):
    """DB Model for harmonic function Verwandschaft."""

    __tablename__ = "harmonische_funktion_verwandschaft"

    display_name = "Harmonische Funktion, Verwandtschaftsgrad"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(
        db.Integer,
        db.ForeignKey("harmonische_funktion_verwandschaft.id", ondelete="CASCADE"),
    )
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)

    parent = relationship(
        lambda: HarmonischeFunktionVerwandschaft,
        remote_side=[id],
        lazy="select",
        join_depth=1,
        back_populates="children",
    )
    children = relationship(
        lambda: HarmonischeFunktionVerwandschaft,
        passive_deletes="all",
        lazy="selectin",
        join_depth=8,
        back_populates="parent",
    )


class HarmonischePhaenomene(db.Model, TreeTaxonomy):
    """DB Model for harmonic phenomenons."""

    __tablename__ = "harmonische_phaenomene"

    display_name = "Harmonische Phänomene"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(
        db.Integer, db.ForeignKey("harmonische_phaenomene.id", ondelete="CASCADE")
    )
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)

    parent = relationship(
        lambda: HarmonischePhaenomene,
        remote_side=[id],
        lazy="select",
        join_depth=1,
        back_populates="children",
    )
    children = relationship(
        lambda: HarmonischePhaenomene,
        passive_deletes="all",
        lazy="selectin",
        join_depth=8,
        back_populates="parent",
    )


class HarmonischeKomplexitaet(db.Model, ListTaxonomy):
    """DB Model for choices."""

    __tablename__ = "harmonische_komplexitaet"

    display_name = "Harmonische Komplexität"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class HarmonischeDichte(db.Model, ListTaxonomy):
    """DB Model for choices."""

    __tablename__ = "harmonische_dichte"

    display_name = "Harmonische Dichte"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class AnzahlMelodietoene(db.Model, ListTaxonomy):
    """DB Model for choices."""

    __tablename__ = "anzahl_melodietoene"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
