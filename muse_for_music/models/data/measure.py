from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin


class Measure(db.Model, GetByID, UpdateableModelMixin):

    _normal_attributes = (('from_page', int), ('measure', int))

    id = db.Column(db.Integer, primary_key=True)
    from_page = db.Column(db.Integer, nullable=True)
    measure = db.Column(db.Integer, nullable=False)

    def __init__(self, measure: int, from_page: int = None):
        self.measure = measure
        self.from_page = None
