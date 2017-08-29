from ... import db
from .helper_classes import ListTaxonomy


class AuftretenWerkausschnitt(db.Model, ListTaxonomy):
    """DB Model for choices."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class AuftretenSatz(db.Model, ListTaxonomy):
    """DB Model for choices."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class Anteil(db.Model, ListTaxonomy):
    """DB Model for choices."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class Frequenz(db.Model, ListTaxonomy):
    """DB Model for choices."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
