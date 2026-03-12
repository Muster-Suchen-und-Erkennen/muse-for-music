from sqlalchemy.orm import Mapped, MappedColumn, relationship

from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin, UpdateListMixin
from ..taxonomies import Grundton, Oktave


class AmbitusGroup(db.Model, GetByID, UpdateableModelMixin, UpdateListMixin):

    _normal_attributes = (
        ("highest_pitch", Grundton),
        ("highest_octave", Oktave),
        ("lowest_pitch", Grundton),
        ("lowest_octave", Oktave),
    )

    __tablename__ = "ambitus_group"
    id = db.Column(db.Integer, primary_key=True)

    highest_pitch_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Grundton.id), nullable=True
    )
    highest_octave_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Oktave.id), nullable=True
    )
    lowest_pitch_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Grundton.id), nullable=True
    )
    lowest_octave_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Oktave.id), nullable=True
    )

    highest_pitch: Mapped[Grundton] = relationship(
        Grundton, foreign_keys=[highest_pitch_id]
    )
    highest_octave: Mapped[Oktave] = relationship(
        Oktave, foreign_keys=[highest_octave_id]
    )
    lowest_pitch: Mapped[Grundton] = relationship(
        Grundton, foreign_keys=[lowest_pitch_id]
    )
    lowest_octave: Mapped[Oktave] = relationship(Oktave, foreign_keys=[lowest_octave_id])
