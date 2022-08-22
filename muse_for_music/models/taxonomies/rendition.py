from ... import db
from .helper_classes import ListTaxonomy, TreeTaxonomy

__all__ = ['Ausdruck', 'Artikulation', 'Spielanweisung']


class Ausdruck(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'ausdruck'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)


class Artikulation(db.Model, TreeTaxonomy):
    """DB Model for doc."""
    __tablename__ = 'artikulation'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('artikulation.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('Artikulation',
                               passive_deletes='all',
                               lazy='joined',
                               join_depth=8,
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='select',
                                                  join_depth=1
                                                 )
                              )


class Spielanweisung(db.Model, TreeTaxonomy):
    """DB Model for doc."""
    __tablename__ = 'spielanweisung'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('spielanweisung.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('Spielanweisung',
                               passive_deletes='all',
                               lazy='joined',
                               join_depth=8,
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='select',
                                                  join_depth=1
                                                 )
                              )
