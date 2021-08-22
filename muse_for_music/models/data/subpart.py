from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin, UpdateListMixin

from typing import Union

from .part import Part
from .harmonics import Harmonics
from .satz import Satz
from .dynamic import Dynamic
from .tempo import TempoGroup
from .ambitus import AmbitusGroup
from .citations import Citations
from .instrumentation import Instrumentation
from ..taxonomies import Anteil, AuftretenWerkausschnitt, MusikalischeWendung

from typing import Union, Sequence, Dict


class SubPart(db.Model, GetByID, UpdateableModelMixin, UpdateListMixin):

    _normal_attributes = (('label', str),
                          ('occurence_in_part', AuftretenWerkausschnitt),
                          ('share_of_part', Anteil),
                          ('is_tutti', bool),
                          ('dynamic', Dynamic),
                          ('harmonics', Harmonics),
                          ('tempo', TempoGroup),)

    _list_attributes = ('instrumentation', )

    id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=False)
    label = db.Column(db.String(191), nullable=False, default='A')
    occurence_in_part_id = db.Column(db.Integer, db.ForeignKey('auftreten_werkausschnitt.id'), nullable=True)
    share_of_part_id = db.Column(db.Integer, db.ForeignKey('anteil.id'), nullable=True)
    instrumentation_id = db.Column(db.Integer, db.ForeignKey('instrumentation.id'))
    is_tutti = db.Column(db.Boolean, default=False)
    dynamic_id = db.Column(db.Integer, db.ForeignKey('dynamic.id'), nullable=True)
    harmonics_id = db.Column(db.Integer, db.ForeignKey('harmonics.id'), nullable=True)
    tempo_id = db.Column(db.Integer, db.ForeignKey('tempo_group.id'), nullable=True)
    # ambitus_id = db.Column(db.Integer, db.ForeignKey('ambitus_group.id'), nullable=True)

    part = db.relationship(Part, lazy='select', backref=db.backref('subparts', single_parent=True, cascade="all, delete-orphan"))
    occurence_in_part = db.relationship(AuftretenWerkausschnitt, lazy='joined', single_parent=True)
    share_of_part = db.relationship(Anteil, lazy='joined', single_parent=True)
    _instrumentation = db.relationship('Instrumentation', lazy='subquery', single_parent=True, cascade="all, delete-orphan")  # type: Instrumentation
    dynamic = db.relationship(Dynamic, single_parent=True, cascade="all, delete-orphan")
    harmonics = db.relationship(Harmonics, single_parent=True, cascade="all, delete-orphan")
    tempo = db.relationship(TempoGroup, single_parent=True, cascade="all, delete-orphan")
    # ambitus = db.relationship(AmbitusGroup, single_parent=True, cascade="all, delete-orphan")

    _subquery_load = ['dynamic', 'harmonics', 'voices']

    def __init__(self, part_id: Union[int, Part], label: str = 'A', **kwargs):
        if isinstance(part_id, Part):
            self.part = part_id
        else:
            self.part = Part.get_by_id(part_id)
        self.label = label

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
