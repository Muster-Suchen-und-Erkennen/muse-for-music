"""Module containing the root resource of the API."""

from flask_restx import Resource
from . import user_api
from .models import root_model

ns = user_api.namespace('default', path='/')

@ns.route('/')
class RootResource(Resource):

    @ns.doc(security=None)
    @ns.marshal_with(root_model)
    def get(self):
        return 'TODO'
