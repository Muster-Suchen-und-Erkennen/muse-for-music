from typing import Sequence, Union

from sqlalchemy.orm import Mapped, MappedColumn, relationship

from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin, UpdateListMixin
from ..taxonomies import (
    Akkord,
    Dissonanzen,
    Dissonanzgrad,
    Grundton,
    HarmonischeDichte,
    HarmonischeEntwicklung,
    HarmonischeFunktion,
    HarmonischeFunktionVerwandschaft,
    HarmonischeKomplexitaet,
    HarmonischePhaenomene,
    HarmonischeStufe,
    Tonalitaet,
)


class Harmonics(db.Model, GetByID, UpdateListMixin, UpdateableModelMixin):

    _normal_attributes = (
        ("degree_of_dissonance", Dissonanzgrad),
        ("numeric_degree_of_dissonance", float),
        ("harmonic_density", HarmonischeDichte),
        ("numeric_harmonic_density", float),
        ("harmonic_complexity", HarmonischeKomplexitaet),
        ("numeric_harmonic_complexity", float),
        # ('harmonische_funktion', HarmonischeFunktionVerwandschaft),
        ("harmonic_analyse", str),
    )

    _list_attributes = (
        "harmonic_centers",
        "harmonic_changes",
        "harmonic_phenomenons",
        "chords",
        "harmonische_funktion",
    )
    # removed: 'dissonances'

    __tablename__ = "harmonics"
    id = db.Column(db.Integer, primary_key=True)
    # harmonic_function_modulation_id = db.Column(db.Integer, db.ForeignKey('harmonische_funktion_verwandschaft.id'))
    degree_of_dissonance_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Dissonanzgrad.id)
    )
    numeric_degree_of_dissonance: MappedColumn[float | None] = db.Column(
        db.Float, nullable=True
    )
    harmonic_density_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(HarmonischeDichte.id)
    )
    numeric_harmonic_density: MappedColumn[float | None] = db.Column(
        db.Float, nullable=True
    )
    harmonic_complexity_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(HarmonischeKomplexitaet.id)
    )
    numeric_harmonic_complexity: MappedColumn[float | None] = db.Column(
        db.Float, nullable=True
    )
    harmonic_analyse: MappedColumn[str | None] = db.Column(db.Text, nullable=True)

    # harmonische_funktion = relationship('HarmonischeFunktionVerwandschaft', lazy='selectin')
    degree_of_dissonance: Mapped[Dissonanzgrad] = relationship(
        Dissonanzgrad, lazy="selectin"
    )
    harmonic_density: Mapped[HarmonischeDichte] = relationship(
        HarmonischeDichte, lazy="selectin"
    )
    harmonic_complexity: Mapped[HarmonischeKomplexitaet] = relationship(
        HarmonischeKomplexitaet, lazy="selectin"
    )

    # backrefs
    _harmonic_centers: Mapped[list["HarmonicCenter"]] = relationship(
        lambda: HarmonicCenter,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="harmonics",
    )
    _harmonic_phenomenons: Mapped[list["HarmonischePhaenomeneToHarmonics"]] = (
        relationship(
            lambda: HarmonischePhaenomeneToHarmonics,
            lazy="selectin",
            single_parent=True,
            cascade="all, delete-orphan",
            back_populates="harmonics",
        )
    )
    _harmonic_changes: Mapped[list["HarmonischeEntwicklungToHarmonics"]] = relationship(
        lambda: HarmonischeEntwicklungToHarmonics,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="harmonics",
    )
    _special_chords: Mapped[list["AkkordToHarmonics"]] = relationship(
        lambda: AkkordToHarmonics,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="harmonics",
    )
    _dissonances: Mapped[list["DissonanzenToHarmonics"]] = relationship(
        lambda: DissonanzenToHarmonics,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="harmonics",
    )
    _harmonische_funktion: Mapped[list["HarmonischeFunktionToHarmonics"]] = relationship(
        lambda: HarmonischeFunktionToHarmonics,
        lazy="selectin",
        single_parent=True,
        cascade="all, delete-orphan",
        back_populates="harmonics",
    )

    @property
    def harmonic_centers(self):
        return self._harmonic_centers

    @harmonic_centers.setter
    def harmonic_centers(self, harmonic_centers_list: Sequence[dict]):
        old_items = {center.id: center for center in self._harmonic_centers}
        self.update_list(harmonic_centers_list, old_items, HarmonicCenter)

    @property
    def harmonic_phenomenons(self):
        return [mapping.harmonische_phaenomene for mapping in self._harmonic_phenomenons]

    @harmonic_phenomenons.setter
    def harmonic_phenomenons(
        self, harmonic_phenomenons_list: Union[Sequence[int], Sequence[dict]]
    ):
        old_items = {
            mapping.harmonische_phaenomene.id: mapping
            for mapping in self._harmonic_phenomenons
        }
        self.update_list(
            harmonic_phenomenons_list,
            old_items,
            HarmonischePhaenomeneToHarmonics,
            HarmonischePhaenomene,
            "harmonische_phaenomene",
        )

    @property
    def harmonic_changes(self):
        return [mapping.harmonische_entwicklung for mapping in self._harmonic_changes]

    @harmonic_changes.setter
    def harmonic_changes(
        self, harmonic_changes_list: Union[Sequence[int], Sequence[dict]]
    ):
        old_items = {
            mapping.harmonische_entwicklung.id: mapping
            for mapping in self._harmonic_changes
        }
        self.update_list(
            harmonic_changes_list,
            old_items,
            HarmonischeEntwicklungToHarmonics,
            HarmonischeEntwicklung,
            "harmonische_entwicklung",
        )

    @property
    def chords(self):
        return [mapping.akkord for mapping in self._special_chords]

    @chords.setter
    def chords(self, special_chords_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.akkord.id: mapping for mapping in self._special_chords}
        self.update_list(
            special_chords_list, old_items, AkkordToHarmonics, Akkord, "akkord"
        )

    @property
    def dissonances(self):
        return [mapping.dissonanzen for mapping in self._dissonances]

    @dissonances.setter
    def dissonances(self, dissonances_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.dissonanzen.id: mapping for mapping in self._dissonances}
        self.update_list(
            dissonances_list,
            old_items,
            DissonanzenToHarmonics,
            Dissonanzen,
            "dissonanzen",
        )

    @property
    def harmonische_funktion(self):
        return [mapping.harmonische_funktion for mapping in self._harmonische_funktion]

    @harmonische_funktion.setter
    def harmonische_funktion(
        self, harmonische_funktion_list: Union[Sequence[int], Sequence[dict]]
    ):
        old_items = {
            mapping.harmonische_funktion.id: mapping
            for mapping in self._harmonische_funktion
        }
        self.update_list(
            harmonische_funktion_list,
            old_items,
            HarmonischeFunktionToHarmonics,
            HarmonischeFunktionVerwandschaft,
            "harmonische_funktion",
        )


class HarmonicCenter(db.Model, UpdateableModelMixin):

    _normal_attributes = (
        ("grundton", Grundton),
        ("harmonische_stufe", HarmonischeStufe),
        ("tonalitaet", Tonalitaet),
        ("harmonische_funktion", HarmonischeFunktion),
    )

    id: MappedColumn[int] = db.Column(db.Integer, primary_key=True)
    harmonics_id: MappedColumn[int] = db.Column(db.Integer, db.ForeignKey(Harmonics.id))
    grundton_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Grundton.id)
    )
    tonalitaet_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Tonalitaet.id)
    )
    harmonische_funktion_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(HarmonischeFunktion.id)
    )
    harmonische_stufe_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(HarmonischeStufe.id)
    )

    harmonics: Mapped[Harmonics] = relationship(
        Harmonics, lazy="select", back_populates="_harmonic_centers"
    )
    grundton: Mapped[Grundton] = relationship(Grundton, lazy="selectin")
    tonalitaet: Mapped[Tonalitaet] = relationship(Tonalitaet, lazy="selectin")
    harmonische_funktion: Mapped[HarmonischeFunktion] = relationship(
        HarmonischeFunktion, lazy="selectin"
    )
    harmonische_stufe: Mapped[HarmonischeStufe] = relationship(
        HarmonischeStufe, lazy="selectin"
    )

    def __init__(self, harmonics, **kwargs):
        self.harmonics = harmonics
        if kwargs:
            self.update(kwargs)


class HarmonischePhaenomeneToHarmonics(db.Model):
    harmonics_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Harmonics.id), primary_key=True
    )
    harmonische_phaenomene_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(HarmonischePhaenomene.id), primary_key=True
    )

    harmonics: Mapped[Harmonics] = relationship(
        Harmonics, back_populates="_harmonic_phenomenons"
    )
    harmonische_phaenomene: Mapped[HarmonischePhaenomene] = relationship(
        HarmonischePhaenomene, lazy="selectin"
    )

    def __init__(self, harmonics, harmonische_phaenomene, **kwargs):
        self.harmonics = harmonics
        self.harmonische_phaenomene = harmonische_phaenomene


class HarmonischeEntwicklungToHarmonics(db.Model):
    harmonics_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Harmonics.id), primary_key=True
    )
    harmonische_entwicklung_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(HarmonischeEntwicklung.id), primary_key=True
    )

    harmonics: Mapped[Harmonics] = relationship(
        Harmonics, back_populates="_harmonic_changes"
    )
    harmonische_entwicklung: Mapped[HarmonischeEntwicklung] = relationship(
        HarmonischeEntwicklung, lazy="selectin"
    )

    def __init__(self, harmonics, harmonische_entwicklung, **kwargs):
        self.harmonics = harmonics
        self.harmonische_entwicklung = harmonische_entwicklung


class AkkordToHarmonics(db.Model):
    harmonics_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Harmonics.id), primary_key=True
    )
    akkord_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Akkord.id), primary_key=True
    )

    harmonics: Mapped[Harmonics] = relationship(
        Harmonics, back_populates="_special_chords"
    )
    akkord: Mapped[Akkord] = relationship(Akkord, lazy="selectin")

    def __init__(self, harmonics, akkord, **kwargs):
        self.harmonics = harmonics
        self.akkord = akkord


class DissonanzenToHarmonics(db.Model):
    harmonics_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Harmonics.id), primary_key=True
    )
    dissonanzen_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Dissonanzen.id), primary_key=True
    )

    harmonics: Mapped[Harmonics] = relationship(Harmonics, back_populates="_dissonances")
    dissonanzen: Mapped[Dissonanzen] = relationship(Dissonanzen, lazy="selectin")

    def __init__(self, harmonics, dissonanzen, **kwargs):
        self.harmonics = harmonics
        self.dissonanzen = dissonanzen


class HarmonischeFunktionToHarmonics(db.Model):
    harmonics_id: MappedColumn[int] = db.Column(
        db.Integer, db.ForeignKey(Harmonics.id), primary_key=True
    )
    harmonic_function_modulation_id: MappedColumn[int] = db.Column(
        db.Integer,
        db.ForeignKey(HarmonischeFunktionVerwandschaft.id),
        primary_key=True,
    )

    harmonics: Mapped[Harmonics] = relationship(
        Harmonics, back_populates="_harmonische_funktion"
    )
    harmonische_funktion: Mapped[HarmonischeFunktionVerwandschaft] = relationship(
        HarmonischeFunktionVerwandschaft, lazy="selectin"
    )

    def __init__(self, harmonics, harmonische_funktion, **kwargs):
        self.harmonics = harmonics
        self.harmonische_funktion = harmonische_funktion
