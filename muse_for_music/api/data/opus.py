from flask import jsonify, url_for, request
from flask_restplus import Resource, marshal
from sqlalchemy.exc import IntegrityError


from . import api

from .models import opus_post, opus_push, opus_get

from ... import db
from ...models.data.opus import Opus


ns = api.namespace('opus', description='TODO.')


@ns.route('/')
class OpusListResource(Resource):

    @ns.marshal_list_with(opus_get)
    def get(self):
        print(Opus.query.first())
        return Opus.query.all()

    @ns.doc(model=opus_get, body=opus_post)
    def post(self):
        new_opus = Opus(**request.get_json())
        try:
            db.session.add(new_opus)
            db.session.commit()
            return marshal(new_opus, opus_get)
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                return {'error': 'Name not unique!'}, 501
            return {'error': str(err)}, 501


@ns.route('/<int:id>')
class OpusResource(Resource):

    @ns.marshal_with(opus_get)
    def get(self, id):
        return Opus.query.filter_by(id=id).first()
