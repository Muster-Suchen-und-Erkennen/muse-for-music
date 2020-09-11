from csv import DictReader
from logging import Logger
from ... import db
from .helper_classes import TreeTaxonomy, ListTaxonomy


__all__ = ['Instrument', 'InstrumentierungEinbettungQualitaet', 'InstrumentierungEinbettungQuantitaet']


class Instrument(db.Model, TreeTaxonomy):
    """DB Model for instruments."""

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('instrument.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('Instrument',
                               passive_deletes='all',
                               lazy='joined',
                               join_depth=8,
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='select',
                                                  join_depth=1
                                                 )
                              )


class InstrumentierungEinbettungQualitaet(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'instrumentierung_einbettung_qualitaet'

    display_name = 'Instrumentierung, Qualität der Einbettung'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class InstrumentierungEinbettungQuantitaet(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'instrumentierung_einbettung_quantitaet'

    display_name = 'Instrumentierung, Quantität der Einbettung'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
