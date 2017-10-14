
from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin
from ..taxonomies import TempoEinbettung, TempoEntwicklung


class TempoContext(db.Model, GetByID, UpdateableModelMixin):

    _normal_attributes = (('tempo_trend_before', TempoEntwicklung),
                          ('tempo_trend_after', TempoEntwicklung),
                          ('tempo_context_before', TempoEinbettung),
                          ('tempo_context_after', TempoEinbettung))

    __tablename__ = 'tempo_context'
    id = db.Column(db.Integer, primary_key=True)

    tempo_context_before_id = db.Column(db.Integer, db.ForeignKey('tempo_einbettung.id'),
                                        nullable=True)
    tempo_context_after_id = db.Column(db.Integer, db.ForeignKey('tempo_einbettung.id'),
                                       nullable=True)
    tempo_trend_before_id = db.Column(db.Integer, db.ForeignKey('tempo_entwicklung.id'),
                                      nullable=True)
    tempo_trend_after_id = db.Column(db.Integer, db.ForeignKey('tempo_entwicklung.id'),
                                     nullable=True)

    tempo_context_before = db.relationship(TempoEinbettung, foreign_keys=[tempo_context_before_id])
    tempo_context_after = db.relationship(TempoEinbettung, foreign_keys=[tempo_context_after_id])
    tempo_trend_before = db.relationship(TempoEntwicklung, foreign_keys=[tempo_trend_before_id])
    tempo_trend_after = db.relationship(TempoEntwicklung, foreign_keys=[tempo_trend_after_id])
