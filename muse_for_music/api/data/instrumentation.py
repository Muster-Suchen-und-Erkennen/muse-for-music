from flask import jsonify, url_for, request
from flask_restplus import Resource, marshal
from sqlalchemy.exc import IntegrityError


from . import api

from .models import instrumentation_get, instrumentation_put

from ... import db
from ...models.data.instrumentation import Instrumentation

ns = api.namespace('instrumentation', description='TODO.')


@ns.route('/')
class InstrumentationListResource(Resource):

    @ns.marshal_list_with(instrumentation_get)
    def get(self):
        return Instrumentation.query.all()

@ns.route('/<int:id>')
class InstrumentationResource(Resource):

    @ns.marshal_with(instrumentation_get)
    def get(self, id):
        instr = Instrumentation.get_by_id(id)
        return instr

    @ns.doc(model=instrumentation_get, body=instrumentation_put)
    def put(self, id):
        instr = Instrumentation.get_by_id(id)  # type: Instrumentation
        new_instr = request.get_json()
        instr.instruments = new_instr['instruments']
        db.session.add(instr)
        db.session.commit()
        return marshal(instr, instrumentation_put)
