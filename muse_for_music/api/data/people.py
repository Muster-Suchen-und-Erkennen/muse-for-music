"""Module for the persons resource."""


from flask import jsonify, url_for, request
from flask_restplus import Resource, marshal, reqparse, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import literal

from json import dumps

from .. import api


from .models import person_post, person_put, person_get, parse_date

from ... import db
from ...user_api import has_roles, RoleEnum
from ...models.data.people import Person, GenderEnum
from ...models.data.opus import Opus
from ...models.data.citations import PersonToCitations
from ...models.data.history import History, MethodEnum, TypeEnum, Backup

from .backup import to_backup_json

ns = api.namespace('person', description='Resource for persons.', path='/persons')


def check_if_person_exists(name):
    q = Person.query.enable_eagerloads(False).filter(Person.name == name).exists()
    if db.session.query(literal(True)).filter(q).scalar():
        abort(409, 'Name "{}" is already in use!'.format(name))


def check_if_person_is_in_use(person: Person):
    q = Opus.query.enable_eagerloads(False).filter(Opus.composer == person).exists()
    if db.session.query(literal(True)).filter(q).scalar():
        abort(409, 'Can not delete Person "{}" beacause it is still in use!'.format(person.name))
    q = PersonToCitations.query.enable_eagerloads(False).filter(PersonToCitations.person == person).exists()
    if db.session.query(literal(True)).filter(q).scalar():
        abort(409, 'Can not delete Person "{}" beacause it is still in use!'.format(person.name))


@ns.route('/')
class PersonListResource(Resource):

    @ns.marshal_list_with(person_get)
    @jwt_required
    def get(self):
        return Person.query.all()

    @ns.doc(model=person_get, body=person_post)
    @ns.response(409, 'Name is not unique.')
    @jwt_required
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def post(self):
        check_if_person_exists(request.get_json()['name'])
        new_person = Person(**request.get_json())
        try:
            db.session.add(new_person)
            hist = History(MethodEnum.create, new_person)
            db.session.add(hist)
            db.session.commit()
            return marshal(new_person, person_get)
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500, str(err))


@ns.route('/<int:id>/')
class PersonResource(Resource):

    @ns.marshal_with(person_get)
    @ns.response(404, 'Person not found.')
    @jwt_required
    def get(self, id):
        person = Person.query.filter_by(id=id).first()
        if person is None:
            abort(404, 'Requested person not found!')
        return person

    @ns.doc(model=person_get, body=person_put, vaidate=True)
    @ns.response(404, 'Person not found.')
    @jwt_required
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def put(self, id):
        person = Person.query.filter_by(id=id).first()  # type: Person
        if person is None:
            abort(404, 'Requested person not found!')
        new_values = request.get_json()

        check_if_person_exists(new_values['name'])

        attrs = ('name', 'canonical_name')
        for attribute in attrs:
            if attribute in new_values:
                setattr(person, attribute, new_values[attribute])

        for attribute in ('birth_date', 'death_date'):
            if attribute in new_values:
                value = parse_date(new_values[attribute])
                setattr(person, attribute, value)

        if 'gender' in new_values:
            value = GenderEnum[new_values['gender']]
            person.gender = value

        db.session.add(person)
        hist = History(MethodEnum.update, person)
        db.session.add(hist)
        db.session.commit()
        return marshal(person, person_get)

    @ns.response(404, 'Person not found.')
    @jwt_required
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def delete(self, id):
        person = Person.query.filter_by(id=id).first()
        if person is None:
            abort(404, 'Requested person not found!')
        check_if_person_is_in_use(person)
        hist = History(MethodEnum.delete, person)
        db.session.add(hist)
        backup = Backup(TypeEnum.person, dumps(to_backup_json(person)))
        db.session.add(backup)
        db.session.delete(person)
        db.session.commit()
