"""
Models for taxonomies.

Two tree models because of bugs in flask restplus:
https://github.com/noirbizarre/flask-restplus/issues/280
https://github.com/noirbizarre/flask-restplus/issues/293

Use tree_model_json for documentation:
@api.response(200, 'Success', tree_model_json)

Use tree_model for marshalling:
return marshal(test, tree_model), 200
"""


from flask_restplus import fields, marshal
from . import ns
from ..models import with_curies

from ...hal_field import HaLUrl, NestedFields, EmbeddedFields, NestedModel, UrlData


# Two tree models because of bugs in flask restplus:
# https://github.com/noirbizarre/flask-restplus/issues/280
# https://github.com/noirbizarre/flask-restplus/issues/293

# Use tree_model_json for documentation:
# @api.response(200, 'Success', tree_model_json)

tree_model_json = ns.schema_model('TreeModelJSON', {
    'required': ['name'],
    'title': 'TreeModelJSON',
    'type': 'object',
    'properties': {
        'name': {
            'type': 'string'
        },
        'children': {
            'type': 'array',
            'items': {
                '$ref': '#/definitions/TreeModelJSON'
            }
        }
    }
})


# Use tree_model for marshalling:
# return marshal(test, tree_model), 200

tree_model = ns.model('TreeModel', {
    'id': fields.String(),
    'name': fields.String(),
})

tree_model['children'] = fields.List(fields.Nested(tree_model), default=[])


# model for list items:
list_item_model = ns.model('ListItemModel', {
    'id': fields.String(),
    'name': fields.String(),
})


class TaxonomyItems(fields.Raw):

    def format(self, items):
        if callable(items):
            items = items()
        if isinstance(items, list):
            return marshal(items, list_item_model)
        else:
            return marshal(items, tree_model)

    def schema(self):
        # does not work with swagger api!
        schema = {}
        listRef = '#/definitions/{0}'.format(list_item_model.name)
        treeRef = '#/definitions/{0}'.format(tree_model.name)
        schema['oneOf'] = [
            {'type': 'array', 'items': {'$ref': listRef}},
            {'$ref': treeRef},
        ]

        return schema


# models for taxonomies
taxonomy_links = ns.model('TaxonomyLinks', {
    'self': HaLUrl(UrlData('api.taxonomies_taxonomy_resource', absolute=True,
                           url_data={'taxonomy': '__name__'}),
                   required=False,),
    'collection': HaLUrl(UrlData('api.taxonomies_taxonomy_list_resource', absolute=True),
                         required=False),
})

taxonomy_model = ns.model('TaxonomyModel', {
    'name': fields.String(required=True, attribute='__name__'),
    '_links': NestedFields(taxonomy_links),
    'taxonomy_type': fields.String(enum=['list', 'tree'], discriminator=True, readonly=None),
    'select_only_leafs': fields.Boolean(default=False, readonly=None, required=False),
    'items': TaxonomyItems(required=False),
}, mask='{name,_links,taxonomy_type,select_only_leafs}')


# models for list of taxonomies:
taxonomy_list_links = ns.inherit('TaxonomyListLinks', with_curies, {
    'self': HaLUrl(UrlData('api.taxonomies_taxonomy_list_resource', absolute=True), required=False),
    'rel:taxonomy': HaLUrl(UrlData('api.taxonomies_taxonomy_list_resource', absolute=True,
                                   templated=True, path_variables=['taxonomy']),
                           required=False),
})

taxonomy_list_resource = ns.model('TaxonomyList', {
    '_links': NestedFields(taxonomy_list_links),
    '_embedded': EmbeddedFields({
        'taxonomy': NestedModel(taxonomy_model, 'taxonomies', True),
    }),
})

