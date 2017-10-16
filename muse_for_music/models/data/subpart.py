from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin

from typing import Union

from .measure import Measure
from .part import Part
from .form import Form
from .harmonics import Harmonics
from .satz import Satz
from .dramaturgic_context import DramaturgicContext
from .dynamic import Dynamic, DynamicContext
from .composition import Composition
from .rythm import Rythm
from .instrumentation import InstrumentationContext, Instrumentation
from ..taxonomies import Anteil


class SubPart(db.Model, GetByID, UpdateableModelMixin):

    _normal_attributes = (('label', str),
                          ('occurence_in_part', Anteil),
                          ('dynamic', Dynamic),
                          ('composition', Composition),
                          ('instrumentation_context', InstrumentationContext),
                          ('satz', Satz),
                          ('harmonics', Harmonics),
                          ('rythm', Rythm),
                          ('dynamic_context', DynamicContext),
                          ('form', Form),
                          ('dramaturgic_context', DramaturgicContext))

    _list_attributes = ('instrumentation',)

    id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('part.id', ondelete='CASCADE'), nullable=False)
    label = db.Column(db.String(5), nullable=False, default='A')
    occurence_in_part_id = db.Column(db.Integer, db.ForeignKey('anteil.id'), nullable=True)
    instrumentation_id = db.Column(db.Integer, db.ForeignKey('instrumentation.id'))
    instrumentation_context_id = db.Column(db.Integer, db.ForeignKey('instrumentation_context.id'), nullable=True)
    satz_id = db.Column(db.Integer, db.ForeignKey('satz.id'), nullable=True)
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'), nullable=True)
    dramaturgic_context_id = db.Column(db.Integer, db.ForeignKey('dramaturgic_context.id'), nullable=True)
    composition_id = db.Column(db.Integer, db.ForeignKey('composition.id'), nullable=True)
    rythm_id = db.Column(db.Integer, db.ForeignKey('rythm.id'), nullable=True)
    dynamic_id = db.Column(db.Integer, db.ForeignKey('dynamic.id'), nullable=True)
    dynamic_context_id = db.Column(db.Integer, db.ForeignKey('dynamic_context.id'), nullable=True)
    harmonics_id = db.Column(db.Integer, db.ForeignKey('harmonics.id'), nullable=True)

    part = db.relationship(Part, lazy='select', backref=db.backref('subparts', single_parent=True, cascade="all, delete-orphan"))
    occurence_in_part = db.relationship(Anteil, lazy='joined', single_parent=True, cascade="all, delete-orphan")
    _instrumentation = db.relationship('Instrumentation', lazy='subquery', single_parent=True, cascade="all, delete-orphan")  # type: Instrumentation
    instrumentation_context = db.relationship(InstrumentationContext, lazy='subquery', single_parent=True, cascade="all, delete-orphan")
    satz = db.relationship(Satz, single_parent=True, cascade="all, delete-orphan")
    form = db.relationship(Form, single_parent=True, cascade="all, delete-orphan")
    dramaturgic_context = db.relationship(DramaturgicContext, single_parent=True, cascade="all, delete-orphan")
    composition = db.relationship(Composition, single_parent=True, cascade="all, delete-orphan")
    rythm = db.relationship(Rythm, single_parent=True, cascade="all, delete-orphan")
    dynamic = db.relationship(Dynamic, single_parent=True, cascade="all, delete-orphan")
    dynamic_context = db.relationship(DynamicContext, single_parent=True, lazy='subquery', cascade="all, delete-orphan")
    harmonics = db.relationship(Harmonics, single_parent=True, cascade="all, delete-orphan")

    _subquery_load = ['satz', 'form', 'dramaturgic_context', 'composition', 'rythm',
                      'dynamic', 'harmonics']

    def __init__(self, part_id: Union[int, Part], label: str = 'A', **kwargs):
        if isinstance(part_id, Part):
            self.part = part_id
        else:
            self.part = Part.get_by_id(part_id)
        self.label = label

        self.form = Form()
        db.session.add(self.form)

        self.satz = Satz()
        db.session.add(self.satz)

        self._instrumentation = Instrumentation()
        db.session.add(self._instrumentation)

    @property
    def instrumentation(self):
        return self._instrumentation.instruments

    @instrumentation.setter
    def instrumentation(self, data: list):
        self._instrumentation.instruments = data
