
from ... import db
from ..helper_classes import GetByID
from ..taxonomies import Lautstaerke, LautstaerkeEinbettung


class DynamicContext(db.Model, GetByID):
    __tablename__ = 'dynamic_context'
    id = db.Column(db.Integer, primary_key=True)

    loudness_before_id = db.Column(db.Integer, db.ForeignKey('lautstaerke.id'),
                                   nullable=True)
    loudness_after_id = db.Column(db.Integer, db.ForeignKey('lautstaerke.id'),
                                  nullable=True)
    dynamic_trend_before_id = db.Column(db.Integer,
                                        db.ForeignKey('lautstaerke_einbettung.id'),
                                        nullable=True)
    dynamic_trend_after_id = db.Column(db.Integer,
                                       db.ForeignKey('lautstaerke_einbettung.id'),
                                       nullable=True)

    loudness_before = db.relationship(Lautstaerke, foreign_keys=[loudness_before_id])
    loudness_after = db.relationship(Lautstaerke, foreign_keys=[loudness_after_id])
    dynamic_trend_before = db.relationship(LautstaerkeEinbettung,
                                           foreign_keys=[dynamic_trend_before_id])
    dynamic_trend_after = db.relationship(LautstaerkeEinbettung,
                                          foreign_keys=[dynamic_trend_after_id])
