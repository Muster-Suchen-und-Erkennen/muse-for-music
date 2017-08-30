from ... import db
from ..helper_classes import GetByID


class Instrumentation(db.Model, GetByID):
    id = db.Column(db.Integer, primary_key=True)

    @property
    def instruments(self):
        return [mapping.instrument for mapping in self._instruments]


class InstumentationToInstrument(db.Model):
    instrumentation_id = db.Column(db.Integer, db.ForeignKey('instrumentation.id'), primary_key=True)
    instrument_id = db.Column(db.Integer, db.ForeignKey('instrument.id'), primary_key=True)

    instrumentation = db.relationship(Instrumentation, backref=db.backref('_instruments', lazy='joined'))
    instrument = db.relationship('Instrument')

