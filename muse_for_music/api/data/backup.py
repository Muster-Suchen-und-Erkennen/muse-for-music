from flask import jsonify, url_for, request
from flask_restx import Resource, marshal, abort
from flask_jwt_extended import jwt_required, get_jwt_claims
from sqlalchemy.exc import IntegrityError

from functools import singledispatch

from . import api

from .models import opus_get, part_get, subpart_get, voice_get, person_get

from ... import db
from ...user_api import has_roles, RoleEnum
from ...models.data.people import Person
from ...models.data.opus import Opus
from ...models.data.part import Part
from ...models.data.subpart import SubPart
from ...models.data.voice import Voice



ns = api.namespace('backup', description='Resource for backups.', path='/backup')


@singledispatch
def to_backup_json(obj):
    return


@to_backup_json.register(Person)
def opus_to_backup_json(obj: Person):
    serializable = marshal(obj, person_get)
    return serializable


@to_backup_json.register(Opus)
def opus_to_backup_json(obj: Opus):
    serializable = marshal(obj, opus_get)
    serializable['parts'] = [to_backup_json(part) for part in obj.parts]
    return serializable


@to_backup_json.register(Part)
def part_to_backup_json(obj: Part):
    serializable = marshal(obj, part_get)
    serializable['subparts'] = [to_backup_json(subpart) for subpart in obj.subparts]
    return serializable


@to_backup_json.register(SubPart)
def subpart_to_backup_json(obj: SubPart):
    print(obj)
    serializable = marshal(obj, subpart_get)
    serializable['voices'] = [to_backup_json(voice) for voice in obj.voices]
    return serializable


@to_backup_json.register(Voice)
def voice_to_backup_json(obj: Voice):
    serializable = marshal(obj, voice_get)
    return serializable
