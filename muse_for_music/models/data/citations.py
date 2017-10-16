from ... import db
from ..taxonomies import Verarbeitungstechnik, Intervall, BewegungImTonraum
from ..helper_classes import GetByID, UpdateListMixin, UpdateableModelMixin

from typing import Union, Sequence, List

class Citations(db.Model, GetByID, UpdateListMixin, UpdateableModelMixin):

    #_normal_attributes = (('nr_varied_repetitions', int), ('nr_exact_repetitions', int))
    #_list_attributes = ('sequences',)

    __tablename__ = 'citations'
    id = db.Column(db.Integer, primary_key=True)
    is_foreign = db.Column(db.Boolean, default=False)

