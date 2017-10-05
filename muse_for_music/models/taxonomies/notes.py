from ... import db
from .helper_classes import ListTaxonomy

__all__ = ['Grundton', 'Intervall']


class Grundton(db.Model, ListTaxonomy):
    """DB Model for choices."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class Intervall(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'intervall'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
