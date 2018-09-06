from ... import db
from .helper_classes import ListTaxonomy


__all__ = ['GattungNineteenthCentury', 'Gattung']


class GattungNineteenthCentury(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'gattung_nineteenth_century'

    display_name = 'Gattung (19. Jh.)'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class Gattung(db.Model, ListTaxonomy):
    """DB Model for choices."""

    display_name = 'Gattung (Bezugnahmen)'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
