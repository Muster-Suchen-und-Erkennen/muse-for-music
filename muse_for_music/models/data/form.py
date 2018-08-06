from ... import db
from ..taxonomies import Formschema, FormaleFunktion
from ..helper_classes import GetByID, UpdateableModelMixin, UpdateListMixin

from typing import Union, Sequence, List


class Form(db.Model, GetByID, UpdateableModelMixin, UpdateListMixin):

    _normal_attributes = (('contains_theme', bool),
                          ('form_schema', Formschema))

    _list_attributes = ('formal_functions', )

    __tablename__ = 'form'
    id = db.Column(db.Integer, primary_key=True)
    form_schema_id = db.Column(db.Integer, db.ForeignKey('formschema.id'), nullable=True)
    contains_theme = db.Column(db.Boolean, default=False)

    form_schema = db.relationship(Formschema)

    @property
    def formal_functions(self):
        return [mapping.formale_funktion for mapping in self._formal_functions]

    @formal_functions.setter
    def formal_functions(self, formal_functions_list: Union[Sequence[int], Sequence[dict]]):
        old_items = {mapping.formale_funktion.id: mapping for mapping in self._formal_functions}
        self.update_list(formal_functions_list, old_items, FormaleFunktionToForm,
                         FormaleFunktion, 'formale_funktion')


class FormaleFunktionToForm(db.Model):
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'), primary_key=True)
    formale_funktion_id = db.Column(db.Integer, db.ForeignKey('formale_funktion.id'), primary_key=True)

    form = db.relationship(Form, backref=db.backref('_formal_functions', lazy='joined', single_parent=True, cascade='all, delete-orphan'))
    formale_funktion = db.relationship('FormaleFunktion')

    def __init__(self, form, formale_funktion, **kwargs):
        self.form = form
        self.formale_funktion = formale_funktion
