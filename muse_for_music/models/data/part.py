from ... import db
from ..helper_classes import GetByID

from .measure import Measure
from .opus import Opus
from .instrumentation import InstrumentationContext
from ..taxonomies import Anteil


class Part(db.Model, GetByID):
    id = db.Column(db.Integer, primary_key=True)
    opus_id = db.Column(db.Integer, db.ForeignKey('opus.id'), nullable=False)
    movement = db.Column(db.Integer, nullable=False)
    measure_start_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    measure_end_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    occurence_in_movement_id = db.Column(db.Integer, db.ForeignKey('anteil.id'), nullable=True)
    instrumentation_context_id = db.Column(db.Integer, db.ForeignKey('instrumentation_context.id'), nullable=True)

    opus = db.relationship(Opus, lazy='select', backref=db.backref('parts'))
    measure_start = db.relationship(Measure, foreign_keys=[measure_start_id], lazy='joined')
    measure_end = db.relationship(Measure, foreign_keys=[measure_end_id], lazy='joined')
    occurence_in_movement = db.relationship(Anteil, lazy='joined')
    instrumentation_context = db.relationship(InstrumentationContext, lazy='joined')

    def __init__(self, opus_id: int, measure_start: dict, measure_end: dict,
                 occurence_in_movement, movement: int=1):
        self.opus = Opus.get_by_id(opus_id)
        self.movement = movement
        self.measure_start = Measure(**measure_start)
        self.measure_end = Measure(**measure_end)
        db.session.add(self.measure_start)
        db.session.add(self.measure_end)
        if isinstance(occurence_in_movement, dict):
            occurence_in_movement = occurence_in_movement['id']
        self.occurence_in_movement = Anteil.get_by_id(occurence_in_movement)
