from ... import db
from ..taxonomies import Formschema, FormaleFunktion
from ..helper_classes import GetByID


class Form(db.Model, GetByID):
    __tablename__ = 'form'
    id = db.Column(db.Integer, primary_key=True)
    form_schema_id = db.Column(db.Integer, db.ForeignKey('formschema.id'), nullable=True)
    formal_function_id = db.Column(db.Integer, db.ForeignKey('formale_funktion.id'), nullable=True)
    contains_theme = db.Column(db.Boolean, server_default=db.text('TRUE'))

    form_schema = db.relationship(Formschema)
    formal_function = db.relationship(FormaleFunktion)
