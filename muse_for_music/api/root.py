"""Module containing the root resource of the API."""

from flask_restplus import Resource
from . import api
from .models import root_model

ns = api.namespace('default', path='/', description='Root Resource')

@ns.route('/')
@ns.doc(security=None)
class RootResource(Resource):

    @ns.marshal_with(root_model)
    def get(self):
        return 'TODO'
