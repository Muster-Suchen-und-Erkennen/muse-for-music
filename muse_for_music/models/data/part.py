from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin, UpdateListMixin

from .measure import Measure
from .opus import Opus
from .instrumentation import InstrumentationContext
from .dynamic import DynamicContext
from .tempo import TempoContext
from .dramaturgic_context import DramaturgicContext
from ..taxonomies import AuftretenSatz, FormaleFunktion

from typing import Union, Sequence, List


class Part(db.Model, GetByID, UpdateableModelMixin, UpdateListMixin):

    _normal_attributes = (('name', str),
                          ('measure_start', Measure),
                          ('measure_end', Measure),
                          ('length', int),
                          ('movement', int),
                          ('dramaturgic_context', DramaturgicContext),
                          ('tempo_context', TempoContext),
                          ('dynamic_context', DynamicContext),
                          ('instrumentation_context', InstrumentationContext))

    _list_attributes = ('formal_functions', 'occurence_in_movement')

    id = db.Column(db.Integer, primary_key=True)
    opus_id = db.Column(db.Integer, db.ForeignKey('opus.id'), nullable=False)
    name = db.Column(db.String(191), nullable=True)
    movement = db.Column(db.Integer, nullable=False)
    measure_start_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    measure_end_id = db.Column(db.Integer, db.ForeignKey('measure.id'), nullable=False)
    length = db.Column(db.Integer, nullable=False)
    #occurence_in_movement_id = db.Column(db.Integer, db.ForeignKey('auftreten_satz.id'), nullable=True)
    instrumentation_context_id = db.Column(db.Integer, db.ForeignKey('instrumentation_context.id'), nullable=True)
    dynamic_context_id = db.Column(db.Integer, db.ForeignKey('dynamic_context.id'), nullable=True)
    tempo_context_id = db.Column(db.Integer, db.ForeignKey('tempo_context.id'), nullable=True)
    dramaturgic_context_id = db.Column(db.Integer, db.ForeignKey('dramaturgic_context.id'), nullable=True)

    opus = db.relationship(Opus, lazy='select', backref=db.backref('parts', cascade="all, delete-orphan"))
    measure_start = db.relationship(Measure, foreign_keys=[measure_start_id], lazy='joined', single_parent=True, cascade="all, delete-orphan")
    measure_end = db.relationship(Measure, foreign_keys=[measure_end_id], lazy='joined', single_parent=True, cascade="all, delete-orphan")
    #occurence_in_movement = db.relationship(AuftretenSatz, lazy='joined')
    instrumentation_context = db.relationship(InstrumentationContext, single_parent=True, cascade="all, delete-orphan")
    dynamic_context = db.relationship(DynamicContext, single_parent=True, cascade="all, delete-orphan")
    tempo_context = db.relationship(TempoContext, single_parent=True, cascade="all, delete-orphan")
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

        from .subpart import SubPart
        from .history import History, MethodEnum

        subpart = SubPart(self)
        db.session.add(subpart)

        hist = History(MethodEnum.create, subpart)
        db.session.add(hist)

    @property
    def formal_functions(self):
        return [mapping.formale_funktion for mapping in self._formal_functions]

    @formal_functions.setter
    def formal_functions(self, formal_functions_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.formale_funktion.id: mapping for mapping in self._formal_functions}
        self.update_list(formal_functions_list, old_items, FormaleFunktionToPart,
                         FormaleFunktion, 'formale_funktion')

    @property
    def occurence_in_movement(self):
        return [mapping.auftreten_satz for mapping in self._occurence_in_movement]

    @occurence_in_movement.setter
    def occurence_in_movement(self, occurence_in_movement_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.auftreten_satz.id: mapping for mapping in self._occurence_in_movement}
        self.update_list(occurence_in_movement_list, old_items, AuftretenSatzToPart,
                        AuftretenSatz, 'auftreten_satz')


class FormaleFunktionToPart(db.Model):
    part_id = db.Column(db.Integer, db.ForeignKey('part.id'), primary_key=True)
    formale_funktion_id = db.Column(db.Integer, db.ForeignKey('formale_funktion.id', name='fk_formale_funktion_to_part_formale_funktion_id'), primary_key=True)

    part = db.relationship(Part, backref=db.backref('_formal_functions', lazy='joined', single_parent=True, cascade='all, delete-orphan'))
    formale_funktion = db.relationship('FormaleFunktion')

    def __init__(self, part, formale_funktion, **kwargs):
        self.part = part
        self.formale_funktion = formale_funktion

class AuftretenSatzToPart(db.Model):
    part_id = db.Column(db.Integer, db.ForeignKey('part.id'), primary_key=True)
    auftreten_satz_id = db.Column(db.Integer, db.ForeignKey('auftreten_satz.id', name='fk_auftreten_satz_to_part_auftreten_satz_id'), primary_key=True)

    part = db.relationship(Part, backref=db.backref('_occurence_in_movement', lazy='joined', single_parent=True, cascade='all, delete-orphan'))
    auftreten_satz = db.relationship('AuftretenSatz')

    def __init__(self, part, auftreten_satz, **kwargs):
        self.part = part
        self.auftreten_satz = auftreten_satz
