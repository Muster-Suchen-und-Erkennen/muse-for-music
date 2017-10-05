from ... import db
from .helper_classes import ListTaxonomy

__all__ = ['Melodiebewegung']


class Melodiebewegung(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'melodiebewegung'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
