from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin, UpdateListMixin

from typing import Union

from .measure import Measure
from .part import Part
from .form import Form
from .harmonics import Harmonics
from .satz import Satz
from .dramaturgic_context import DramaturgicContext
from .dynamic import Dynamic, DynamicContext
from .composition import Composition
from .rhythm import Rhythm
from .tempo import TempoGroup
from .rendition import Rendition
from .citations import Citations
from .instrumentation import InstrumentationContext, Instrumentation
from ..taxonomies import Anteil, AuftretenWerkausschnitt, MusikalischeWendung

from typing import Union, Sequence, Dict


class SubPart(db.Model, GetByID, UpdateableModelMixin, UpdateListMixin):

    _normal_attributes = (('label', str),
                          ('occurence_in_part', AuftretenWerkausschnitt),
                          ('share_of_part', Anteil),
                          ('dynamic', Dynamic),
                          ('composition', Composition),
                          ('instrumentation_context', InstrumentationContext),
                          ('satz', Satz),
                          ('harmonics', Harmonics),
                          ('rhythm', Rhythm),
                          ('dynamic_context', DynamicContext),
                          ('form', Form),
                          ('dramaturgic_context', DramaturgicContext),
                          ('tempo', TempoGroup),
                          ('rendition', Rendition),
                          ('citations', Citations))

    _list_attributes = ('instrumentation', 'musicial_figures')

    id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=False)
    label = db.Column(db.String(5), nullable=False, default='A')
    occurence_in_part_id = db.Column(db.Integer, db.ForeignKey('auftreten_werkausschnitt.id'), nullable=True)
    share_of_part_id = db.Column(db.Integer, db.ForeignKey('anteil.id'), nullable=True)
    instrumentation_id = db.Column(db.Integer, db.ForeignKey('instrumentation.id'))
    instrumentation_context_id = db.Column(db.Integer, db.ForeignKey('instrumentation_context.id'), nullable=True)
    satz_id = db.Column(db.Integer, db.ForeignKey('satz.id'), nullable=True)
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'), nullable=True)
    dramaturgic_context_id = db.Column(db.Integer, db.ForeignKey('dramaturgic_context.id'), nullable=True)
    composition_id = db.Column(db.Integer, db.ForeignKey('composition.id'), nullable=True)
    rhythm_id = db.Column(db.Integer, db.ForeignKey('rhythm.id'), nullable=True)
    dynamic_id = db.Column(db.Integer, db.ForeignKey('dynamic.id'), nullable=True)
    dynamic_context_id = db.Column(db.Integer, db.ForeignKey('dynamic_context.id'), nullable=True)
    harmonics_id = db.Column(db.Integer, db.ForeignKey('harmonics.id'), nullable=True)
    tempo_id = db.Column(db.Integer, db.ForeignKey('tempo_group.id'), nullable=True)
    rendition_id = db.Column(db.Integer, db.ForeignKey('rendition.id'), nullable=True)
    citations_id = db.Column(db.Integer, db.ForeignKey('citations.id'), nullable=True)

    part = db.relationship(Part, lazy='select', backref=db.backref('subparts', single_parent=True, cascade="all, delete-orphan"))
    occurence_in_part = db.relationship(AuftretenWerkausschnitt, lazy='joined', single_parent=True)
    share_of_part = db.relationship(Anteil, lazy='joined', single_parent=True)
    _instrumentation = db.relationship('Instrumentation', lazy='subquery', single_parent=True, cascade="all, delete-orphan")  # type: Instrumentation
    instrumentation_context = db.relationship(InstrumentationContext, lazy='subquery', single_parent=True, cascade="all, delete-orphan")
    satz = db.relationship(Satz, single_parent=True, cascade="all, delete-orphan")
    form = db.relationship(Form, single_parent=True, cascade="all, delete-orphan")
    dramaturgic_context = db.relationship(DramaturgicContext, single_parent=True, cascade="all, delete-orphan")
    composition = db.relationship(Composition, single_parent=True, cascade="all, delete-orphan")
    rhythm = db.relationship(Rhythm, single_parent=True, cascade="all, delete-orphan")
    dynamic = db.relationship(Dynamic, single_parent=True, cascade="all, delete-orphan")
    dynamic_context = db.relationship(DynamicContext, single_parent=True, lazy='subquery', cascade="all, delete-orphan")
    harmonics = db.relationship(Harmonics, single_parent=True, cascade="all, delete-orphan")
    tempo = db.relationship(TempoGroup, single_parent=True, cascade="all, delete-orphan")
    rendition = db.relationship(Rendition, single_parent=True, cascade="all, delete-orphan")
    citations = db.relationship(Citations, single_parent=True, cascade="all, delete-orphan")

    _subquery_load = ['satz', 'form', 'dramaturgic_context', 'composition', 'rhythm',
                      'dynamic', 'harmonics', 'voices']

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

    @property
    def musicial_figures(self):
        return [mapping.musikalische_wendung for mapping in self._musicial_figures]

    @musicial_figures.setter
    def musicial_figures(self, musicial_figures_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.musikalische_wendung.id: mapping for mapping in self._musicial_figures}
        self.update_list(musicial_figures_list, old_items, MusikalischeWendungToSubPart,
                         MusikalischeWendung, 'musikalische_wendung')


class MusikalischeWendungToSubPart(db.Model):
    sub_part_id = db.Column(db.Integer, db.ForeignKey('sub_part.id'), primary_key=True)
    musikalische_wendung_id = db.Column(db.Integer, db.ForeignKey('musikalische_wendung.id'), primary_key=True)

    sub_part = db.relationship(SubPart, backref=db.backref('_musicial_figures', lazy='joined', single_parent=True, cascade='all, delete-orphan'))
    musikalische_wendung = db.relationship('MusikalischeWendung')

    def __init__(self, sub_part, musikalische_wendung, **kwargs):
        self.sub_part = sub_part
        self.musikalische_wendung = musikalische_wendung
