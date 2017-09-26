from ... import db
from ..helper_classes import GetByID

from .measure import Measure
from .part import Part
from .instrumentation import InstrumentationContext
#from .dynamic import DynamicContext
#from .tempo import TempoContext
#from ..taxonomies import Anteil


class SubPart(db.Model, GetByID):
    id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=False)
    label = db.Column(db.String(1), nullable=False)
    occurence_in_part_id = db.Column(db.Integer, db.ForeignKey('anteil.id'), nullable=True)

    part = db.relationship(Part, lazy='select', backref=db.backref('subparts'))
    occurence_in_part = db.relationship(Anteil, lazy='joined')
    #instrumentation_context = db.relationship(InstrumentationContext, lazy='joined')
    #dynamic_context = db.relationship(DynamicContext, lazy='joined')
    #tempo_context = db.relationship(TempoContext, lazy='joined')

    def __init__(self, part_id: int, label: str='A'):
        self.part = Part.get_by_id(part_id)
        self.label = label
