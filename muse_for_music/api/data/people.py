from flask import jsonify, url_for, request
from flask_restplus import Resource, marshal, reqparse


from . import ns

from .models import person_model

from ... import db
from ...models.data.people import Person


parser = reqparse.RequestParser()
parser.add_argument('person', location='json')


@ns.route('/person')
class ChordsResource(Resource):

    @ns.marshal_list_with(person_model)
    def get(self):
        return Person.query.all()

    @ns.expect(parser)
    def post(self):
        new_person = Person(**request.get_json())
        db.session.add(new_person)
        db.session.commit()

