from ... import db
from ..taxonomies import SatzartAllgemein, SatzartSpeziell
from ..helper_classes import GetByID, UpdateableModelMixin


class Satz(db.Model, GetByID, UpdateableModelMixin):

    _normal_attributes = (('satzart_allgemein', SatzartAllgemein), ('satzart_speziell', SatzartSpeziell))

    __tablename__ = 'satz'
    id = db.Column(db.Integer, primary_key=True)
    satzart_allgemein_id = db.Column(db.Integer, db.ForeignKey('satzart_allgemein.id'), nullable=True)
    satzart_speziell_id = db.Column(db.Integer, db.ForeignKey('satzart_speziell.id'), nullable=True)

    satzart_allgemein = db.relationship(SatzartAllgemein, lazy='joined')
    satzart_speziell = db.relationship(SatzartSpeziell, lazy='joined')
