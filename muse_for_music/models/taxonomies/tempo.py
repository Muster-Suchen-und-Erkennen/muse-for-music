
from ... import db
from .helper_classes import TreeTaxonomy, ListTaxonomy


__all__ = ['Tempo', 'TempoEntwicklung', 'TempoEinbettung']


class Tempo(db.Model, TreeTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'tempo'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('tempo.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('Tempo',
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='joined',
                                                  join_depth=1
                                                 )
                              )


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
