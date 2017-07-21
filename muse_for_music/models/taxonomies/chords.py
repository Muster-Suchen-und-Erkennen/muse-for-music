from csv import DictReader
from logging import Logger
from ... import db
from .helper_classes import TreeTaxonomy


class Akkord(db.Model, TreeTaxonomy):
    """DB Model for chords."""

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('akkord.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    children = db.relationship('Akkord',
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='joined',
                                                  join_depth=1
                                                 )
                              )
