from ... import db
from ..taxonomies import Formschema
from ..helper_classes import GetByID


class Form(db.Model, GetByID):
    __tablename__ = 'form'
    id = db.Column(db.Integer, primary_key=True)
    form_schema_id = db.Column(db.Integer, db.ForeignKey('formschema.id'), nullable=True)

    form_schema = db.relationship(Formschema)
