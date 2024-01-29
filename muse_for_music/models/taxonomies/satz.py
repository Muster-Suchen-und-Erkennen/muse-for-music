from ... import db
from .helper_classes import ListTaxonomy

__all__ = ['SatzartAllgemein', 'SatzartSpeziell']


class SatzartAllgemein(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'satzart_allgemein'

    display_name = 'Satzart allgemein'
    specification = 'aa'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class SatzartSpeziell(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'satzart_speziell'

    display_name = 'Satzart Speziell'
    specification = 'aa'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
