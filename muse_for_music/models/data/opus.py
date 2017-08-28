from ... import db

from ..taxonomies.gattung import GattungNineteenthCentury
from .instrumentation import Instrumentation


class Opus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, index=True)
    original_name = db.Column(db.String(255), unique=True, index=True, nullable=True)
    opus_name = db.Column(db.String(255), index=True, nullable=True)
    composer = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=True)
    # TODO add mitarbeiter
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

    instrumentation = db.relationship('Instrumentation', lazy='joined')
    # TODO form
    genre = db.relationship('GattungNineteenthCentury', lazy='joined')

    def __init__(self, name: str, movements:int =1, printed: bool=False, **kwargs) -> None:
        self.name = name
        self.printed = printed
        self.movements = movements
        for key in kwargs:
            if key in ('original_name', 'opus_name', 'composition_date',
                       'occasion', 'dedication', 'notes', 'first_printed_in',
                       'publisher'):
                setattr(self, key, kwargs[key])

        self.instrumentation = Instrumentation()

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