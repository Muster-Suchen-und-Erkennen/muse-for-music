
from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin, UpdateListMixin
from ..taxonomies import Grundton, Oktave

from typing import Union, Sequence, Dict


class AmbitusGroup(db.Model, GetByID, UpdateableModelMixin, UpdateListMixin):

    _normal_attributes = (('highest_pitch', Grundton),
                          ('highest_octave', Oktave),
                          ('lowest_pitch', Grundton),
                          ('lowest_octave', Oktave), )

    __tablename__ = 'ambitus_group'
    id = db.Column(db.Integer, primary_key=True)

    highest_pitch_id = db.Column(db.Integer, db.ForeignKey('grundton.id'), nullable=True)
    highest_octave_id = db.Column(db.Integer, db.ForeignKey('oktave.id'), nullable=True)
    lowest_pitch_id = db.Column(db.Integer, db.ForeignKey('grundton.id'), nullable=True)
    lowest_octave_id = db.Column(db.Integer, db.ForeignKey('oktave.id'), nullable=True)

    highest_pitch = db.relationship(Grundton, foreign_keys=[highest_pitch_id])
    highest_octave = db.relationship(Oktave, foreign_keys=[highest_octave_id])
    lowest_pitch = db.relationship(Grundton, foreign_keys=[lowest_pitch_id])
    lowest_octave = db.relationship(Oktave, foreign_keys=[lowest_octave_id])
