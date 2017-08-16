from ... import db


class Instrumentation(db.Model):
    id = db.Column(db.Integer, primary_key=True)


class InstumentationToInstrument(db.Model):
    instrumentation_id = db.Column(db.Integer, db.ForeignKey('instrumentation.id'), primary_key=True)
    instrument_id = db.Column(db.Integer, db.ForeignKey('instrument.id'), primary_key=True)

    instrumentation = db.relationship('Instrumentation', backref=db.backref('instruments', lazy='joined'))
    instrumentation = db.relationship('Instrument')

