"""Module for the opus resource."""


from flask import jsonify, url_for, request
from flask_restplus import Resource, marshal, abort
from sqlalchemy.exc import IntegrityError


from . import api

from .models import opus_post, opus_put, opus_get, parse_date, opus_get, opus_post, \
                    part_get, part_post

from ... import db
from ...models.data.opus import Opus
from ...models.data.part import Part


ns = api.namespace('opus', description='Resource for opuses.')


@ns.route('/')
class OpusListResource(Resource):

    @ns.marshal_list_with(opus_get)
    def get(self):
        return Opus.query.all()

    @ns.doc(model=opus_get, body=opus_post)
    @ns.response(409, 'Name is not unique.')
    def post(self):
        new_opus = Opus(**request.get_json())
        try:
            db.session.add(new_opus)
            db.session.commit()
            return marshal(new_opus, opus_get)
        except IntegrityError as err:
            message = str(err)
            if 'UNIQUE constraint failed' in message:
                abort(409, 'Name is not unique!')
            abort(500, str(err))


@ns.route('/<int:id>')
class OpusResource(Resource):

    @ns.marshal_with(opus_get)
    @ns.response(404, 'Opus not found.')
    def get(self, id):
        opus = Opus.get_by_id(id)  # type: Opus
        if opus is None:
            abort(404, 'Requested opus not found!')
        return opus

    @ns.doc(model=opus_get, body=opus_put)
    @ns.response(404, 'Opus not found.')
    def put(self, id):
        opus = Opus.get_by_id(id)  # type: Opus
        if opus is None:
            abort(404, 'Requested opus not found!')
        new_values = request.get_json()

        opus.update(new_values)
        db.session.commit()
        return marshal(opus, opus_get)

    @ns.response(404, 'Opus not found.')
    def delete(self, id):
        opus = Opus.get_by_id(id)  # type: Opus
        if opus is None:
            abort(404, 'Requested opus not found!')
        db.session.delete(opus)
        db.session.commit()




@ns.route('/<int:id>/parts')
class OpusPartsResource(Resource):

    @ns.marshal_list_with(part_get)
    def get(self, id):
        parts = Part.query.filter_by(opus_id=id).all()
        print('M'*100)
        print(parts[0].measure_end.from_page, type(parts[0].measure_end.from_page))
        return parts

    @ns.doc(model=part_get, body=part_post)
    def post(self, id):
        new_values = request.get_json()
        new_values['opus_id'] = id
        new_part = Part(**new_values)
        db.session.add(new_part)
        db.session.commit()
        return marshal(new_part, part_get)
