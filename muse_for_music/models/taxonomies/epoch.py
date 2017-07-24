from ... import db
from .helper_classes import ListTaxonomy


class Epoche(db.Model, ListTaxonomy):
    """DB Model for choices."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))


