from flask_restplus import Resource
from . import api

ns = api.namespace('default', path='/')

@ns.route('/')
class RootResource(Resource):


    def get(self):
        return 'TODO'
