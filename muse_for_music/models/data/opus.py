from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin

from ..taxonomies import Grundton, Tonalitaet, GattungNineteenthCentury
from .people import Person


class Opus(db.Model, GetByID, UpdateableModelMixin):

    _normal_attributes = (('name', str),
                          ('original_name', str),
                          ('composer', Person),
                          ('score_link', str),
                          ('first_printed_at', int),
                          ('first_printed_in', int),
                          ('composition_year', int),
                          ('composition_place', str),
                          ('first_played_at', int),
                          ('first_played_in', int),
                          ('notes', str),
                          ('movements', int),
                          ('genre', GattungNineteenthCentury),
                          ('grundton', Grundton),
                          ('tonalitaet', Tonalitaet))

    _reference_only_attributes = ('composer', )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, index=True)
    original_name = db.Column(db.String(255), unique=True, index=True, nullable=True)
    composer_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=True)
    score_link = db.Column(db.Text, nullable=True)
    first_printed_at = db.Column(db.String(255), nullable=True)  # TODO Foreign key
    first_printed_in = db.Column(db.Integer, nullable=True)
    composition_year = db.Column(db.Integer, nullable=True)
    composition_place = db.Column(db.String(255), nullable=True)  # TODO Foreign key
    first_played_at = db.Column(db.String(255), nullable=True)  # TODO Foreign key
    first_played_in = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    movements = db.Column(db.Integer)
    genre_id = db.Column(db.Integer, db.ForeignKey('gattung_nineteenth_century.id'))
    grundton_id = db.Column(db.Integer, db.ForeignKey('grundton.id'))
    tonalitaet_id = db.Column(db.Integer, db.ForeignKey('tonalitaet.id'))

    composer = db.relationship('Person', lazy='select')
    genre = db.relationship(GattungNineteenthCentury, lazy='joined')
    grundton = db.relationship('Grundton', lazy='joined')
    tonalitaet = db.relationship('Tonalitaet', lazy='joined')
    # TODO metadata

    _subquery_load = ['composer', 'parts']

    def __init__(self, name: str, composer: any=None, movements:int =1,
                 printed: bool=False, **kwargs) -> None:
        self.name = name
        self.movements = movements
        for key in kwargs:
            if key in ('original_name', 'composition_date', 'notes', 'first_printed_in',):
                setattr(self, key, kwargs[key])

        if composer:
            composer_id = None
            if isinstance(composer, int):
                composer_id = composer
            else:
                composer_id = composer.get('id')
            if composer_id is not None:
                comp = Person.get_by_id(composer_id)  # type: Person
                self.composer = comp
            else:
                self.composer = Person(**composer)
                db.session.add(self.composer)

        if 'genre' in kwargs:
            genre = GattungNineteenthCentury.query.filter_by(name=kwargs['genre']).first()
            if genre:
                self.genre = genre

    def __repr__(self):
        return '<Werk %r>' % self.name
