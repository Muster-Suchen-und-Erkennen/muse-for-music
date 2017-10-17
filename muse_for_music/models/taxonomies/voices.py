
from ... import db
from .helper_classes import TreeTaxonomy, ListTaxonomy


__all__ = ['MusikalischeFunktion', 'Verzierung', 'VoiceToVoiceRelation']


class MusikalischeFunktion(db.Model, TreeTaxonomy):
    """DB Model for doc."""
    __tablename__ = 'musikalische_funktion'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('musikalische_funktion.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('MusikalischeFunktion',
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='joined',
                                                  join_depth=1
                                                 )
                              )


class Verzierung(db.Model, TreeTaxonomy):
    """DB Model for doc."""
    __tablename__ = 'verzierung'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('verzierung.id', ondelete='CASCADE'))
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
    children = db.relationship('Verzierung',
                               backref=db.backref('parent',
                                                  remote_side=[id],
                                                  lazy='joined',
                                                  join_depth=1
                                                 )
                              )


class VoiceToVoiceRelation(db.Model, ListTaxonomy):
    """DB Model for choices."""
    __tablename__ = 'voice_to_voice_relation'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text(), nullable=True)
