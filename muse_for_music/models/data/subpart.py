from ... import db
from ..helper_classes import GetByID

from typing import Union

from .measure import Measure
from .part import Part
from .form import Form
from .satz import Satz
from .dramaturgic_context import DramaturgicContext
from .composition import Composition
from .instrumentation import InstrumentationContext, Instrumentation
from ..taxonomies import Anteil
#from .dynamic import DynamicContext
#from .tempo import TempoContext
#from ..taxonomies import Anteil


class SubPart(db.Model, GetByID):
    id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=False)
    label = db.Column(db.String(5), nullable=False)
    occurence_in_part_id = db.Column(db.Integer, db.ForeignKey('anteil.id'), nullable=True)
    instrumentation_id = db.Column(db.Integer, db.ForeignKey('instrumentation.id'))
    instrumentation_context_id = db.Column(db.Integer, db.ForeignKey('instrumentation_context.id'), nullable=True)
    satz_id = db.Column(db.Integer, db.ForeignKey('satz.id'), nullable=True)
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'), nullable=True)
    dramaturgic_context_id = db.Column(db.Integer, db.ForeignKey('dramaturgic_context.id'), nullable=True)
    composition_id = db.Column(db.Integer, db.ForeignKey('composition.id'), nullable=True)

    part = db.relationship(Part, lazy='select', backref=db.backref('subparts'))
    occurence_in_part = db.relationship(Anteil, lazy='joined')
    _instrumentation = db.relationship('Instrumentation', lazy='subquery')  # type: Instrumentation
    instrumentation_context = db.relationship(InstrumentationContext, lazy='subquery')
    satz = db.relationship(Satz)
    form = db.relationship(Form)
    dramaturgic_context = db.relationship(DramaturgicContext)
    composition = db.relationship(Composition)

    _subquery_load = ['satz', 'form', 'dramaturgic_context', 'composition']

    def __init__(self, part_id: Union[int, Part], label: str='A'):
        if isinstance(part_id, Part):
            self.part = part_id
        else:
            self.part = Part.get_by_id(part_id)
        self.label = label

        self.form = Form()
        db.session.add(self.form)

        self.satz = Satz()
        db.session.add(self.satz)

    @property
    def instrumentation(self):
        return self._instrumentation.instruments

    @instrumentation.setter
    def instrumentation(self, data: list):
        self._instrumentation.instruments = data
