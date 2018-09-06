from ... import db
from .helper_classes import ListTaxonomy

__all__ = ['AuftretenWerkausschnitt', 'AuftretenSatz', 'Anteil', 'Frequenz', 'BewegungImTonraum']


class AuftretenWerkausschnitt(db.Model, ListTaxonomy):
    """DB Model for choices."""

    display_name = 'Auftreten im Werkausschnitt'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class AuftretenSatz(db.Model, ListTaxonomy):
    """DB Model for choices."""

    display_name = 'Auftreten im Satz'

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


class BewegungImTonraum(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'bewegung_im_tonraum'

    display_name = 'Bewegung im Tonraum'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
