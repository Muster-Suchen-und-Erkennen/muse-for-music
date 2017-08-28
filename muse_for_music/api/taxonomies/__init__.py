from flask_restplus import Resource, marshal, abort

from ...models.taxonomies import get_taxonomies
from .. import api

ns = api.namespace('taxonomies', description='All Taxonomies.')

from .models import taxonomy_list_resource, taxonomy_model, list_taxonomy_model, tree_taxonomy_model, tree_taxonomy_model_json


taxonomies = get_taxonomies()


@ns.route('/')
class TaxonomyListResource(Resource):


    @ns.marshal_with(taxonomy_list_resource)
    def get(self):
        taxonomy_list = list(taxonomies.values())
        return{'taxonomies': taxonomy_list}


def get_taxonomy(taxonomy_type: str, taxonomy_name: str):
        taxonomy_name = taxonomy_name.upper()
        if taxonomy_name not in taxonomies:
            abort(404, 'The reqested Taxonomy could not be found.')
        taxonomy = taxonomies[taxonomy_name]
        if taxonomy_type != taxonomy.taxonomy_type:
            abort(400, 'The type of the requested taxonomy does not match the requested taxonomy type. (requested type: {}, taxonomy_type: {})'
                  .format(taxonomy_type, taxonomy.taxonomy_type))
        return taxonomy



@ns.route('/<string:taxonomy_type>/<string:taxonomy>', doc=False)
class TaxonomyResource(Resource):

    taxonomies = get_taxonomies()

    @ns.marshal_with(taxonomy_model)
    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy not found.')
    def get(self, taxonomy_type: str, taxonomy: str):
        return get_taxonomy(taxonomy_type, taxonomy)


@ns.route('/list/<string:taxonomy>')
class ListTaxonomyResource(Resource):

    taxonomies = get_taxonomies()

    @ns.marshal_with(list_taxonomy_model)
    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy not found.')
    def get(self, taxonomy: str):
        return get_taxonomy('list', taxonomy)


@ns.route('/tree/<string:taxonomy>')
class TreeTaxonomyResource(Resource):

    taxonomies = get_taxonomies()

    @ns.response('200', 'success', tree_taxonomy_model_json)
    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy not found.')
    def get(self, taxonomy: str):
        return marshal(get_taxonomy('tree', taxonomy), tree_taxonomy_model)

