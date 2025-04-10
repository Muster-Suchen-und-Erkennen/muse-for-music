from ... import db
from ..helper_classes import GetByID, UpdateableModelMixin


class Measure(db.Model, GetByID, UpdateableModelMixin):

    _normal_attributes = (('from_page', int), ('measure', int))
    _optional_attributes = ('from_page', )

    id = db.Column(db.Integer, primary_key=True)
    _from_page = db.Column(db.Integer, nullable=True)
    measure = db.Column(db.Integer, nullable=False)

    def __init__(self, measure: int = 1, from_page: int = None, **kwargs):
        self.measure = measure
        self.from_page = from_page

    @property
    def from_page(self):
        return self._from_page if self._from_page is not None else -1

    @from_page.setter
    def from_page(self, value):
        if value is None:
            self._from_page = None
            return
        self._from_page = value if value > 0 else None
