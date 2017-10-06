from ... import db
from .helper_classes import ListTaxonomy, TreeTaxonomy

__all__ = ['Taktart', 'Rhythmustyp', 'RhythmischesPhaenomen']


class Taktart(db.Model, TreeTaxonomy):
    """DB Model for taktart."""
    __tablename__ = 'taktart'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('taktart.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('Taktart',
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='joined',
                                                  join_depth=1
                                                 )
                              )


class Rhythmustyp(db.Model, TreeTaxonomy):
    """DB Model for rythm type."""
    __tablename__ = 'rhythmustyp'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('rhythmustyp.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('Rhythmustyp',
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='joined',
                                                  join_depth=1
                                                 )
                              )


class RhythmischesPhaenomen(db.Model, TreeTaxonomy):
    """DB Model for rythmic phenomenon."""
    __tablename__ = 'rhythmisches_phaenomen'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('rhythmisches_phaenomen.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('RhythmischesPhaenomen',
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='joined',
                                                  join_depth=1
                                                 )
                              )
