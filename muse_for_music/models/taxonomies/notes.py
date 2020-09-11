from ... import db
from .helper_classes import ListTaxonomy, TreeTaxonomy

__all__ = ['Grundton', 'Notenwert', 'Intervall', 'Intervallik', 'Oktave']


class Grundton(db.Model, ListTaxonomy):
    """DB Model for choices."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class Oktave(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'oktave'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class Notenwert(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'notenwert'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class Intervall(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'intervall'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class Intervallik(db.Model, TreeTaxonomy):
    """DB Model for doc."""
    __tablename__ = 'intervallik'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('intervallik.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('Intervallik',
                               passive_deletes='all',
                               lazy='joined',
                               join_depth=8,
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='select',
                                                  join_depth=1
                                                 )
                              )
