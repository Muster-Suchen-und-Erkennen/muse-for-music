from ... import db
from .helper_classes import ListTaxonomy

class GattungNineteenthCentury(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'gattung_nineteenth_century'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))


class Gattung(db.Model, ListTaxonomy):
    """DB Model for choices."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
