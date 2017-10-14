from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin

from ..taxonomies.gattung import GattungNineteenthCentury
from .instrumentation import Instrumentation
from .people import Person


class Opus(db.Model, GetByID, UpdateableModelMixin):

    _normal_attributes = (('opus_name', str), ('composition_year', int),
                          ('notes', str), ('score_link', str), ('publisher', str),
                          ('printed', bool), ('composer', Person), ('name', str),
                          ('occasion', str), ('original_name', str),
                          ('movements', int), ('genre', GattungNineteenthCentury),
                          ('first_printed_in', int), ('dedication', str))

    _reference_only_attributes = ('composer', )

    _list_attributes = ('instrumentation', )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, index=True)
    original_name = db.Column(db.String(255), unique=True, index=True, nullable=True)
    opus_name = db.Column(db.String(255), index=True, nullable=True)
    composer_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=True)
    # TODO add mitarbeiter
    score_link = db.Column(db.Text, nullable=True)
    composition_year = db.Column(db.Integer, nullable=True)
    composition_place_id = db.Column(db.Integer, nullable=True)  # TODO Foreign key
    occasion = db.Column(db.Text, nullable=True)
    dedication = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    printed = db.Column(db.Boolean)
    first_printed_at_id = db.Column(db.Integer, nullable=True)  # TODO Foreign key
    first_printed_in = db.Column(db.Integer, nullable=True)
    publisher = db.Column(db.String(255), index=True, nullable=True)
    instrumentation_id = db.Column(db.Integer, db.ForeignKey('instrumentation.id'))
    movements = db.Column(db.Integer)
    #form = db.Column(db.Integer, db.ForeignKey('.id'))  # TODO Foreign key
    genre_id = db.Column(db.Integer, db.ForeignKey('gattung_nineteenth_century.id'))

    composer = db.relationship('Person', lazy='select')
    _instrumentation = db.relationship('Instrumentation', lazy='subquery')  # type: Instrumentation
    # TODO form
    genre = db.relationship(GattungNineteenthCentury, lazy='joined')
    # TODO metadata

    _subquery_load = ['composer', 'parts']

    def __init__(self, name: str, composer: any=None, movements:int =1,
                 printed: bool=False, **kwargs) -> None:
        self.name = name
        self.printed = printed
        self.movements = movements
        for key in kwargs:
            if key in ('original_name', 'opus_name', 'composition_date',
                       'occasion', 'dedication', 'notes', 'first_printed_in',
                       'publisher'):
                setattr(self, key, kwargs[key])

        if composer:
            composer_id = None
            if isinstance(composer, int):
                composer_id = composer
            else:
                composer_id = composer.get('id')
            if composer_id is not None:
                comp = Person.query.filter_by(id=id).first()  # type: Person
                self.composer = comp

        self._instrumentation = Instrumentation()

        if 'instrumentation' in kwargs:
            pass  # TODO load instrumentation

        if 'form' in kwargs:
            pass  # TODO load form

        if 'genre' in kwargs:
            genre = GattungNineteenthCentury.query.filter_by(name=kwargs['genre']).first()
            if genre:
                self.genre = genre

    def __repr__(self):
        return '<Werk %r>' % self.name

    @property
    def instrumentation(self):
        return self._instrumentation.instruments

    @instrumentation.setter
    def instrumentation(self, data: list):
        self._instrumentation.instruments = data
