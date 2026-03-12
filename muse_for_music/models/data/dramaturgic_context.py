from sqlalchemy.orm import Mapped, MappedColumn, relationship

from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin
from ..taxonomies import AmbitusEinbettung, AmbitusEntwicklung, Melodiebewegung


class DramaturgicContext(db.Model, GetByID, UpdateableModelMixin):

    _normal_attributes = (
        ("ambitus_context_before", AmbitusEinbettung),
        ("melodic_line_before", Melodiebewegung),
        ("ambitus_change_before", AmbitusEntwicklung),
        ("ambitus_change_after", AmbitusEntwicklung),
        ("melodic_line_after", Melodiebewegung),
        ("ambitus_context_after", AmbitusEinbettung),
    )

    __tablename__ = "dramaturgic_context"
    id = db.Column(db.Integer, primary_key=True)
    ambitus_context_before_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(AmbitusEinbettung.id), nullable=True
    )
    ambitus_context_after_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(AmbitusEinbettung.id), nullable=True
    )
    ambitus_change_before_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(AmbitusEntwicklung.id), nullable=True
    )
    ambitus_change_after_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(AmbitusEntwicklung.id), nullable=True
    )
    melodic_line_before_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Melodiebewegung.id), nullable=True
    )
    melodic_line_after_id: MappedColumn[int | None] = db.Column(
        db.Integer, db.ForeignKey(Melodiebewegung.id), nullable=True
    )

    ambitus_context_before: Mapped[AmbitusEinbettung] = relationship(
        AmbitusEinbettung, foreign_keys=[ambitus_context_before_id]
    )
    ambitus_context_after: Mapped[AmbitusEinbettung] = relationship(
        AmbitusEinbettung, foreign_keys=[ambitus_context_after_id]
    )
    ambitus_change_before: Mapped[AmbitusEntwicklung] = relationship(
        AmbitusEntwicklung, foreign_keys=[ambitus_change_before_id]
    )
    ambitus_change_after: Mapped[AmbitusEntwicklung] = relationship(
        AmbitusEntwicklung, foreign_keys=[ambitus_change_after_id]
    )
    melodic_line_before: Mapped[Melodiebewegung] = relationship(
        Melodiebewegung, foreign_keys=[melodic_line_before_id]
    )
    melodic_line_after: Mapped[Melodiebewegung] = relationship(
        Melodiebewegung, foreign_keys=[melodic_line_after_id]
    )
