from ... import db
from .helper_classes import ListTaxonomy, TreeTaxonomy

__all__ = ['Melodiebewegung', 'Melodieform']


class Melodiebewegung(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'melodiebewegung'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class Melodieform(db.Model, TreeTaxonomy):
    """DB Model for doc."""
    __tablename__ = 'melodieform'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('melodieform.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('Melodieform',
                               passive_deletes='all',
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='joined',
                                                  join_depth=1
                                                 )
                              )
