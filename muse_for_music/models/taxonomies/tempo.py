
from ... import db
from .helper_classes import TreeTaxonomy, ListTaxonomy


__all__ = ['Tempo', 'TempoEntwicklung', 'TempoEinbettung']


class Tempo(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'tempo'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class TempoEntwicklung(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'tempo_entwicklung'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class TempoEinbettung(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'tempo_einbettung'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)