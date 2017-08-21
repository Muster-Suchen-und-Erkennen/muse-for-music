from flask_restplus import Resource, marshal

from ...models.taxonomies import get_taxonomies
from .. import api

ns = api.namespace('taxonomies', description='All Taxonomies.')

from .models import taxonomy_list_resource, taxonomy_model


@ns.route('/')
class TaxonomyListResource(Resource):

    taxonomies = get_taxonomies()

    @ns.marshal_with(taxonomy_list_resource)
    def get(self):
        taxonomies = list(self.taxonomies.values())
        return{'taxonomies': taxonomies}


@ns.route('/<string:taxonomy>')
class TaxonomyResource(Resource):

    taxonomies = get_taxonomies()

    @ns.marshal_with(taxonomy_model, mask='{*}')
    def get(self, taxonomy: str):
        taxonomy = taxonomy.upper()
        if taxonomy not in self.taxonomies:
            pass
        tax = self.taxonomies[taxonomy]
        return tax

