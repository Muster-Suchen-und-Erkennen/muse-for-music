"""Module for the voice root resource."""

from flask_jwt_extended import jwt_required
from flask_restx import Resource

from ... import db
from ...models.data.voice import Voice
from . import api
from .models import voice_small

ns = api.namespace(
    "voice", description="List resource to access all available voices.", path="/voices"
)


@ns.route("/")
class VoiceListResource(Resource):

    @ns.marshal_list_with(voice_small)
    @jwt_required()
    def get(self):
        q = Voice.prepare_query(lazy=True)
        return db.session.execute(q).scalars().all()
