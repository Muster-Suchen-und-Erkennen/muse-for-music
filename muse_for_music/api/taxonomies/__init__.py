from flask_restplus import fields, Resource

from .. import api
from ..models import api_resource

ns = api.namespace('taxonomies', description='All Taxonomies.')

from . import instruments
from . import chords
from . import misc


chord_resource = ns.inherit('ChordResource', api_resource, {
    'uri': fields.Url('api.taxonomies_chords_resource', absolute=True),
    'uri_https': fields.Url('api.taxonomies_chords_resource', absolute=True, scheme='https'),
})

instruments_resource = ns.inherit('InstrumentResource', api_resource, {
    'uri': fields.Url('api.taxonomies_instrument_resource', absolute=True),
    'uri_https': fields.Url('api.taxonomies_instrument_resource', absolute=True, scheme='https'),
})

taxonomy_resource = ns.model('TaxonomiesEndpoints', {
    'chords': fields.Nested(chord_resource),
    'instruments': fields.Nested(instruments_resource),
})


@ns.route('/')
class TaxonomiesResource(Resource):

    @ns.marshal_with(taxonomy_resource)
    def get(self):
        taxonomy_endpoints = {
            'chords': {
                'name': 'chords',
                'description': 'test'
            },
            'instruments': {
                'name': 'instruments',
                'description': 'test'
            }
        }
        return taxonomy_endpoints

