
from ... import db
from .helper_classes import TreeTaxonomy, ListTaxonomy


__all__ = ['Lautstaerke', 'LautstaerkeZusatz', 'LautstaerkeEntwicklung', 'LautstaerkeEinbettung']


class Lautstaerke(db.Model, ListTaxonomy):
    """DB Model for choices."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class LautstaerkeZusatz(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'lautstaerke_zusatz'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class LautstaerkeEntwicklung(db.Model, TreeTaxonomy):
    """DB Model for dynamic evolution."""
    __tablename__ = 'lautstaerke_entwicklung'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('lautstaerke_entwicklung.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('LautstaerkeEntwicklung',
                               passive_deletes='all',
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='joined',
                                                  join_depth=1
                                                 )
                              )


class LautstaerkeEinbettung(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'lautstaerke_einbettung'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
