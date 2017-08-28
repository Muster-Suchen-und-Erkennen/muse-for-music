from flask import jsonify, url_for, request
from flask_restplus import Resource, marshal, reqparse, abort
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


from .. import api


from .models import person_post, person_push, person_get

from ... import db
from ...models.data.people import Person

ns = api.namespace('person', description='TODO.')


@ns.route('/')
class PersonListResource(Resource):

    @ns.marshal_list_with(person_get)
    def get(self):
        return Person.query.all()

    @ns.doc(model=person_get, body=person_post)
    @ns.response(409, 'Name is not unique.')
    def post(self):
        new_person = Person(**request.get_json())
        try:
            db.session.add(new_person)
            db.session.commit()
            return marshal(new_person, person_get)
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500, str(err))


@ns.route('/<int:id>')
class PersonResource(Resource):

    @ns.marshal_with(person_get)
    def get(self, id):
        return Person.query.filter_by(id=id).first()

    def delete(self, id):
        person = Person.query.filter_by(id=id).first()
        db.session.delete(person)
        db.session.commit()
