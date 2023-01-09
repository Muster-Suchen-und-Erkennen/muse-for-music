from ... import db
from .helper_classes import ListTaxonomy, TreeTaxonomy


__all__ = ['SpecAnteil','SpecAuftreten']


class SpecAnteil(db.Model, ListTaxonomy):
    """DB Model for specification Anteil."""
    __tablename__ = 'spezifikation_anteil'

    id=db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class SpecAuftreten(db.Model, ListTaxonomy):
    """DB Model for specification Auftreten."""
    __tablename__ = 'spezifikation_auftreten'

    id=db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
