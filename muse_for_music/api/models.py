from flask_restplus import fields
from . import api


api_route_parameter = api.model('API_RouteParameter', {
    'name': fields.String(required=True),
    'description': fields.String,
    'type': fields.String,
})

api_resource = api.model('API_Resource', {
    'name': fields.String(required=True),
    'description': fields.String,
    'parameters': fields.List(fields.Nested(api_route_parameter)),
    #'uri': fields.Url(),
    #'uri_https': fields.Url(scheme='https'),
})
