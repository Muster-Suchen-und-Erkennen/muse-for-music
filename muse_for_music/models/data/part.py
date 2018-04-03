from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin

from .measure import Measure
from .opus import Opus
from .instrumentation import InstrumentationContext
from .dynamic import DynamicContext
from .tempo import TempoContext
from .form import Form
from .dramaturgic_context import DramaturgicContext
from ..taxonomies import AuftretenSatz


class Part(db.Model, GetByID, UpdateableModelMixin):

    _normal_attributes = (('name', str),
                          ('measure_start', Measure),
                          ('measure_end', Measure),
                          ('length', int),
                          ('movement', int),
                          ('occurence_in_movement', AuftretenSatz),
                          ('form', Form),
                          ('dramaturgic_context', DramaturgicContext),
                          ('tempo_context', TempoContext),
                          ('dynamic_context', DynamicContext),
                          ('instrumentation_context', InstrumentationContext))

    id = db.Column(db.Integer, primary_key=True)
    opus_id = db.Column(db.Integer, db.ForeignKey('opus.id'), nullable=False)
    name = db.Column(db.String(255), nullable=True)
    movement = db.Column(db.Integer, nullable=False)
    measure_start_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    measure_end_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    length = db.Column(db.Integer, nullable=False)
    occurence_in_movement_id = db.Column(db.Integer, db.ForeignKey('auftreten_satz.id'), nullable=True)
    instrumentation_context_id = db.Column(db.Integer, db.ForeignKey('instrumentation_context.id'), nullable=True)
    dynamic_context_id = db.Column(db.Integer, db.ForeignKey('dynamic_context.id'), nullable=True)
    tempo_context_id = db.Column(db.Integer, db.ForeignKey('tempo_context.id'), nullable=True)
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'), nullable=True)
    dramaturgic_context_id = db.Column(db.Integer, db.ForeignKey('dramaturgic_context.id'), nullable=True)

    opus = db.relationship(Opus, lazy='select', backref=db.backref('parts', cascade="all, delete-orphan"))
    measure_start = db.relationship(Measure, foreign_keys=[measure_start_id], lazy='joined', single_parent=True, cascade="all, delete-orphan")
    measure_end = db.relationship(Measure, foreign_keys=[measure_end_id], lazy='joined', single_parent=True, cascade="all, delete-orphan")
    occurence_in_movement = db.relationship(AuftretenSatz, lazy='joined')
    instrumentation_context = db.relationship(InstrumentationContext, single_parent=True, cascade="all, delete-orphan")
    dynamic_context = db.relationship(DynamicContext, single_parent=True, cascade="all, delete-orphan")
    tempo_context = db.relationship(TempoContext, single_parent=True, cascade="all, delete-orphan")
    form = db.relationship(Form, lazy='joined', single_parent=True, cascade="all, delete-orphan")
    dramaturgic_context = db.relationship(DramaturgicContext, single_parent=True, cascade="all, delete-orphan")

    _subquery_load = ['dramaturgic_context', 'tempo_context', 'dynamic_context',
                      'instrumentation_context', 'subparts']

    def __init__(self, opus_id: int, measure_start: dict, measure_end: dict,
                 length: int=1, movement: int=1, name: str='', **kwargs):
        self.opus = Opus.get_by_id(opus_id)
        self.name = name
        self.movement = movement
        self.measure_start = Measure(**measure_start)
        self.measure_end = Measure(**measure_end)
        db.session.add(self.measure_start)
        db.session.add(self.measure_end)
        self.length = length

        self.instrumentation_context = InstrumentationContext()
        self.dynamic_context = DynamicContext()
        self.tempo_context = TempoContext()
        self.dramaturgic_context = DramaturgicContext()
        db.session.add(self.instrumentation_context)
        db.session.add(self.dynamic_context)
        db.session.add(self.tempo_context)
        db.session.add(self.dramaturgic_context)

        self.form = Form()
        db.session.add(self.form)

        from .subpart import SubPart

        subpart = SubPart(self)
        db.session.add(subpart)
