"""Module for the persons resource."""

from json import dumps

from flask import jsonify, request, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource, abort, marshal, reqparse
from sqlalchemy import literal
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.sql import delete, select

from ... import db
from ...models.data.citations import PersonToCitations
from ...models.data.history import Backup, History, MethodEnum, TypeEnum
from ...models.data.opus import Opus
from ...models.data.people import GenderEnum, Person
from ...models.users import User
from ...user_api import RoleEnum, has_roles
from .. import api
from .backup import to_backup_json
from .models import parse_date, person_get, person_post, person_put

ns = api.namespace("person", description="Resource for persons.", path="/persons")


def check_if_person_exists(name):
    q = select(Person).where(Person.name == name).limit(1)
    result = db.session.execute(select(q.exists())).scalar_one_or_none()
    if bool(result):
        abort(409, 'Name "{}" is already in use!'.format(name))


def check_if_person_is_in_use(person: Person):
    q = select(Opus).where(Opus.composer == person).limit(1)
    used_as_composer = db.session.execute(select(q.exists())).scalar_one_or_none()
    if bool(used_as_composer):
        abort(
            409,
            'Can not delete Person "{}" beacause it is still in use!'.format(person.name),
        )
    q = select(PersonToCitations).where(PersonToCitations.person == person).limit(1)
    used_as_citation = db.session.execute(select(q.exists())).scalar_one_or_none()
    if bool(used_as_citation):
        abort(
            409,
            'Can not delete Person "{}" beacause it is still in use!'.format(person.name),
        )


@ns.route("/")
class PersonListResource(Resource):

    @ns.marshal_list_with(person_get)
    @jwt_required()
    def get(self):
        q = select(Person)
        return db.session.execute(q).scalars().all()

    @ns.doc(model=person_get, expect=[person_post], validate=True)
    @ns.response(409, "Name is not unique.")
    @jwt_required()
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def post(self):
        check_if_person_exists(request.get_json()["name"])
        new_person = Person(**request.get_json())
        try:
            db.session.add(new_person)
            hist = History(MethodEnum.create, new_person)
            db.session.add(hist)
            db.session.commit()
            return marshal(new_person, person_get)
        except IntegrityError as err:
            db.session.rollback()
            message = str(err)
            if "UNIQUE constraint failed" in message:
                abort(409, "Name is not unique!")
            abort(500, str(err))


@ns.route("/<int:id>/")
class PersonResource(Resource):

    @ns.marshal_with(person_get)
    @ns.response(404, "Person not found.")
    @jwt_required()
    def get(self, id):
        person = Person.get_by_id(id)
        if person is None:
            abort(404, "Requested person not found!")
        return person

    @ns.doc(model=person_get, expect=[person_put], validate=True)
    @ns.response(404, "Person not found.")
    @jwt_required()
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def put(self, id):
        person = Person.get_by_id(id)
        if person is None:
            abort(404, "Requested person not found!")
        new_values = request.get_json()

        if person.name != new_values["name"]:
            check_if_person_exists(new_values["name"])

        attrs = ("name", "canonical_name", "nationality")
        for attribute in attrs:
            if attribute in new_values:
                setattr(person, attribute, new_values[attribute])

        for attribute in ("birth_date", "death_date"):
            if attribute in new_values:
                value = new_values[attribute]
                setattr(person, attribute, value if value > 0 else None)

        if "gender" in new_values:
            value = GenderEnum[new_values["gender"]]
            person.gender = value

        db.session.add(person)
        username = get_jwt_identity()
        user = User.get_user_by_name(username)
        del_q = delete(History).where(
            History.user_id == user.id,
            History.method == MethodEnum.update,
            History.resource == History.fingerprint(person),
        )
        db.session.execute(del_q)
        hist = History(MethodEnum.update, person, user)
        db.session.add(hist)
        db.session.commit()
        return marshal(person, person_get)

    @ns.response(404, "Person not found.")
    @jwt_required()
    @has_roles([RoleEnum.user, RoleEnum.admin])
    def delete(self, id):
        person = Person.get_by_id(id)
        if person is None:
            abort(404, "Requested person not found!")
        check_if_person_is_in_use(person)
        hist = History(MethodEnum.delete, person)
        db.session.add(hist)
        backup = Backup(TypeEnum.person, dumps(to_backup_json(person)))
        db.session.add(backup)
        db.session.delete(person)
        db.session.commit()
