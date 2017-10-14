from ... import db
from ..taxonomies import Formschema, FormaleFunktion
from ..helper_classes import GetByID, UpdateableModelMixin


class Form(db.Model, GetByID, UpdateableModelMixin):

    _normal_attributes = (('contains_theme', bool),
                          ('formal_function', FormaleFunktion),
                          ('form_schema', Formschema))

    __tablename__ = 'form'
    id = db.Column(db.Integer, primary_key=True)
    form_schema_id = db.Column(db.Integer, db.ForeignKey('formschema.id'), nullable=True)
    formal_function_id = db.Column(db.Integer, db.ForeignKey('formale_funktion.id'), nullable=True)
    contains_theme = db.Column(db.Boolean, default=True)

    form_schema = db.relationship(Formschema)
    formal_function = db.relationship(FormaleFunktion)
