from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin

from .measure import Measure
from .opus import Opus
from .instrumentation import InstrumentationContext
from .dynamic import DynamicContext
from .tempo import TempoContext
from .form import Form
from ..taxonomies import AuftretenSatz, Anteil


class Part(db.Model, GetByID, UpdateableModelMixin):

    _normal_attributes = (('measure_start', Measure),
                          ('measure_end', Measure),
                          ('length', int),
                          ('movement', int),
                          ('occurence_in_movement', Anteil),
                          ('form', Form),
                          ('tempo_context', TempoContext),
                          ('dynamic_context', DynamicContext),
                          ('instrumentation_context', InstrumentationContext))

    id = db.Column(db.Integer, primary_key=True)
    opus_id = db.Column(db.Integer, db.ForeignKey('opus.id'), nullable=False)
    movement = db.Column(db.Integer, nullable=False)
    measure_start_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    measure_end_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    length = db.Column(db.Integer, nullable=False)
    occurence_in_movement_id = db.Column(db.Integer, db.ForeignKey('anteil.id'), nullable=True)
    instrumentation_context_id = db.Column(db.Integer, db.ForeignKey('instrumentation_context.id'), nullable=True)
    dynamic_context_id = db.Column(db.Integer, db.ForeignKey('dynamic_context.id'), nullable=True)
    tempo_context_id = db.Column(db.Integer, db.ForeignKey('tempo_context.id'), nullable=True)
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'), nullable=True)

    opus = db.relationship(Opus, lazy='select', backref=db.backref('parts'))
    measure_start = db.relationship(Measure, foreign_keys=[measure_start_id], lazy='joined')
    measure_end = db.relationship(Measure, foreign_keys=[measure_end_id], lazy='joined')
    occurence_in_movement = db.relationship(Anteil, lazy='joined')
    instrumentation_context = db.relationship(InstrumentationContext, lazy='joined')
    dynamic_context = db.relationship(DynamicContext, lazy='joined')
    tempo_context = db.relationship(TempoContext, lazy='joined')
    form = db.relationship(Form, lazy='joined')

    def __init__(self, opus_id: int, measure_start: dict, measure_end: dict,
                 occurence_in_movement, length: int=1, movement: int=1):
        self.opus = Opus.get_by_id(opus_id)
        self.movement = movement
        self.measure_start = Measure(**measure_start)
        self.measure_end = Measure(**measure_end)
        db.session.add(self.measure_start)
        db.session.add(self.measure_end)
        self.length = length
        if isinstance(occurence_in_movement, dict):
            occurence_in_movement = occurence_in_movement['id']
        self.occurence_in_movement = AuftretenSatz.get_by_id(occurence_in_movement)

        self.instrumentation_context = InstrumentationContext()
        self.dynamic_context = DynamicContext()
        self.tempo_context = TempoContext()
        db.session.add(self.instrumentation_context)
        db.session.add(self.dynamic_context)
        db.session.add(self.tempo_context)

        self.form = Form()
        db.session.add(self.form)

        from .subpart import SubPart

        subpart = SubPart(self)
        db.session.add(subpart)
