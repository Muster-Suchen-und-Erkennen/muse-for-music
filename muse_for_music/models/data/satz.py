from sqlalchemy.orm import backref
from muse_for_music.models.taxonomies import satz
from ... import db
from ..taxonomies import SatzartAllgemein, SatzartSpeziell
from ..helper_classes import GetByID, UpdateableModelMixin

from typing import Union, Sequence, List


class Satz(db.Model, GetByID, UpdateableModelMixin):

    #_normal_attributes = (#('satzart_allgemein', SatzartAllgemein), ('satzart_speziell', SatzartSpeziell))
    _list_attributes = ('satzart_allgemein','satzart_speziell')

    __tablename__ = 'satz'
    id = db.Column(db.Integer, primary_key=True)
    #satzart_allgemein_id = db.Column(db.Integer, db.ForeignKey('satzart_allgemein.id'), nullable=True)
    #satzart_speziell_id = db.Column(db.Integer, db.ForeignKey('satzart_speziell.id'), nullable=True)

    #satzart_allgemein = db.relationship(SatzartAllgemein, lazy='joined')
    #satzart_speziell = db.relationship(SatzartSpeziell, lazy='joined')

    @property
    def satzart_allgemein(self):
        return [mapping.satzart_allgemein for mapping in self._satzart_allgemein]

    @satzart_allgemein.setter
    def satzart_allgemein(self, satzart_allgemein_list:Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.satzart_allgemein.id: mapping for mapping in self._satzart_allgemein}
        self.update_list(satzart_allgemein_list, old_items,SatzartAllgemeinToSatz,
                        SatzartAllgemein, 'SatzartAllgemein')

    @property
    def satzart_speziell(self):
        return [mapping.satzart_speziell for mapping in self._satzart_speziell]

    @satzart_speziell.setter
    def satzart_speziell(self, satzart_speziell_list:Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.satzart_speziell.id: mapping for mapping in self._satzart_speziell}
        self.update_list(satzart_speziell_list, old_items,SatzartSpeziellToSatz,
                        SatzartSpeziell, 'SatzartSpeziell')

class SatzartAllgemeinToSatz(db.Model):
    satz_id = db.Column(db.Integer, db.ForeignKey('satz.id'), primary_key=True)
    satzart_allgemein_id = db.Column(db.Integer, db.ForeignKey('satzart_allgemein.id'), primary_key=True)

    satz = db.relationship(Satz, backref=db.backref('_satzart_allgemein', lazy='joined', single_parent=True, cascade="all, delete-orphan"))
    satzart_allgemein = db.relationship('SatzartAllgemein')

    def __init__(self, satz, satzart_allgemein, **kwargs):
        self.satz = satz
        self.satzart_allgemein = satzart_allgemein

class SatzartSpeziellToSatz(db.Model):
    satz_id = db.Column(db.Integer, db.ForeignKey('satz.id'), primary_key=True)
    satzart_speziell_id = db.Column(db.Integer, db.ForeignKey('satzart_speziell.id'), primary_key=True)

    satz = db.relationship(Satz, backref=db.backref('_satzart_speziell', lazy='joined', single_parent=True, cascade="all, delete-orphan"))
    satzart_speziell = db.relationship('SatzartSpeziell')

    def __init__(self, satz, satzart_speziell, **kwargs):
        self.satz = satz
        self.satzart_speziell = satzart_speziell
