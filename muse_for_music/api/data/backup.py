from functools import singledispatch

from flask_restx import marshal

from ...models.data.opus import Opus
from ...models.data.part import Part
from ...models.data.people import Person
from ...models.data.subpart import SubPart
from ...models.data.voice import Voice
from . import api
from .models import opus_get, part_get, person_get, subpart_get, voice_get

ns = api.namespace("backup", description="Resource for backups.", path="/backup")


@singledispatch
def to_backup_json(obj) -> dict | None:
    return None


@to_backup_json.register(Person)
def person_to_backup_json(obj: Person) -> dict | None:
    serializable = marshal(obj, person_get)  # type: ignore
    assert isinstance(serializable, dict)  # type check assert
    return serializable


@to_backup_json.register(Opus)
def opus_to_backup_json(obj: Opus) -> dict | None:
    serializable: dict = marshal(obj, opus_get)  # type: ignore
    assert isinstance(serializable, dict)  # type check assert
    serializable["parts"] = [to_backup_json(part) for part in obj.parts]
    return serializable


@to_backup_json.register(Part)
def part_to_backup_json(obj: Part) -> dict | None:
    serializable: dict = marshal(obj, part_get)  # type: ignore
    assert isinstance(serializable, dict)  # type check assert
    serializable["subparts"] = [to_backup_json(subpart) for subpart in obj.subparts]
    return serializable


@to_backup_json.register(SubPart)
def subpart_to_backup_json(obj: SubPart) -> dict | None:
    serializable: dict = marshal(obj, subpart_get)  # type: ignore
    assert isinstance(serializable, dict)  # type check assert
    serializable["voices"] = [to_backup_json(voice) for voice in obj.voices]
    return serializable


@to_backup_json.register(Voice)
def voice_to_backup_json(obj: Voice) -> dict | None:
    serializable = marshal(obj, voice_get)
    assert isinstance(serializable, dict)  # type check assert
    return serializable
