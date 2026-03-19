from sqlalchemy.orm import Mapped, MappedColumn, relationship
from sqlalchemy.sql import select

from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin
from ..taxonomies import GattungNineteenthCentury, Grundton, Tonalitaet
from .people import Person


class Opus(db.Model, GetByID, UpdateableModelMixin):

    _normal_attributes = (
        ("name", str),
        ("original_name", str),
        ("composer", Person),
        ("score_link", str),
        ("first_printed_at", int),
        ("first_printed_in", int),
        ("composition_year", int),
        ("composition_place", str),
        ("first_played_at", int),
        ("first_played_in", int),
        ("notes", str),
        ("movements", int),
        ("genre", GattungNineteenthCentury),
        ("grundton", Grundton),
        ("tonalitaet", Tonalitaet),
    )

    _reference_only_attributes = ("composer",)

    id = db.Column(db.Integer, primary_key=True)
    name: MappedColumn[str | None] = db.Column(db.String(191), unique=True, index=True)
    original_name: MappedColumn[str | None] = db.Column(
        db.String(191), index=True, nullable=True
    )
    composer_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Person.id), nullable=True
    )
    score_link: MappedColumn[str | None] = db.Column(db.Text, nullable=True)
    first_printed_at: MappedColumn[str | None] = db.Column(db.String(191), nullable=True)
    first_printed_in: MappedColumn[int | None] = db.Column(db.Integer, nullable=True)
    composition_year: MappedColumn[int | None] = db.Column(db.Integer, nullable=True)
    composition_place: MappedColumn[str | None] = db.Column(db.String(191), nullable=True)
    first_played_at: MappedColumn[str | None] = db.Column(db.String(191), nullable=True)
    first_played_in: MappedColumn[int | None] = db.Column(db.Integer, nullable=True)
    notes: MappedColumn[str | None] = db.Column(db.Text, nullable=True)
    movements: MappedColumn[int | None] = db.Column(db.Integer)
    genre_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(GattungNineteenthCentury.id, ondelete="RESTRICT")
    )
    grundton_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Grundton.id, ondelete="RESTRICT")
    )
    tonalitaet_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Tonalitaet.id, ondelete="RESTRICT")
    )

    composer: Mapped[Person] = relationship(Person, lazy="selectin")
    genre: Mapped[GattungNineteenthCentury] = relationship(
        GattungNineteenthCentury, lazy="selectin"
    )
    grundton: Mapped[Grundton] = relationship(Grundton, lazy="select")
    tonalitaet: Mapped[Tonalitaet] = relationship(Tonalitaet, lazy="select")

    # cross-file backref: Part.opus uses back_populates="parts"
    parts: Mapped[list["Part"]] = relationship(
        lambda: Part,
        cascade="all, delete-orphan",
        back_populates="opus",
    )
    # TODO metadata

    _eager_load = [
        "composer",
        "grundton",
        "tonalitaet",
        "parts",
    ]

    def __init__(  # noqa: C901
        self,
        name: str,
        composer: Person | dict | int | None = None,
        movements: int = 1,
        printed: bool = False,
        **kwargs,
    ) -> None:
        self.name = name
        self.movements = movements
        for key in kwargs:
            if key in (
                "original_name",
                "composition_date",
                "notes",
                "first_printed_in",
            ):
                setattr(self, key, kwargs[key])

        if composer:
            if isinstance(composer, Person):
                self.composer = composer
            elif isinstance(composer, int):
                found_composer = Person.get_by_id(composer)
                if found_composer is None:
                    raise KeyError(f"Did not find person with Person.id=={composer}!")
                self.composer = found_composer
            elif isinstance(composer_id := composer.get("id"), int):
                found_composer = Person.get_by_id(composer_id)
                if found_composer is None:
                    raise KeyError(f"Did not find person with Person.id=={composer_id}!")
                self.composer = found_composer
            else:
                self.composer = Person(**composer)
                db.session.add(self.composer)

        if "genre" in kwargs:
            q = (
                select(GattungNineteenthCentury)
                .where(GattungNineteenthCentury.name == kwargs["genre"])
                .limit(1)
            )
            genre = db.session.execute(q).scalar_one_or_none()
            if genre:
                self.genre = genre

    def __repr__(self):
        return "<Werk %r>" % self.name


from .part import Part  # noqa
