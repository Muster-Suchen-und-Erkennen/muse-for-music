from ... import db
from .helper_classes import ListTaxonomy, TreeTaxonomy

__all__ = ['Zitat', 'Programmgegenstand', 'Tonmalerei']


class Zitat(db.Model, TreeTaxonomy):
    """DB Model for citation."""
    __tablename__ = 'zitat'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('zitat.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('Zitat',
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='joined',
                                                  join_depth=1
                                                 )
                              )


class Programmgegenstand(db.Model, TreeTaxonomy):
    """DB Model for doc."""
    __tablename__ = 'programmgegenstand'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('programmgegenstand.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('Programmgegenstand',
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='joined',
                                                  join_depth=1
                                                 )
                              )


class Tonmalerei(db.Model, TreeTaxonomy):
    """DB Model for doc."""
    __tablename__ = 'tonmalerei'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('tonmalerei.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('Tonmalerei',
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='joined',
                                                  join_depth=1
                                                 )
                              )
