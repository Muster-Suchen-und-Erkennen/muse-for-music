"""
Models for taxonomies.

Two tree models because of bugs in flask restplus:
https://github.com/noirbizarre/flask-restplus/issues/280
https://github.com/noirbizarre/flask-restplus/issues/293

Use taxonomy_tree_item_get_json for documentation:
@api.response(200, 'Success', taxonomy_tree_item_get_json)

Use taxonomy_tree_item_get for marshalling:
return marshal(test, taxonomy_tree_item_get), 200
"""

from collections import OrderedDict
from flask_restplus import fields, marshal
from . import ns
from ..models import with_curies

from ...hal_field import HaLUrl, NestedFields, EmbeddedFields, NestedModel, UrlData


taxonomy_item_links = ns.model('TaxonomyItemLinks', {
    'self': HaLUrl(UrlData('api.taxonomies_taxonomy_item_resource', absolute=True,
                           url_data={'taxonomy': '__class__.__name__',
                                     'taxonomy_type': 'taxonomy_type',
                                     'item_id': 'id'}),
                   required=False),
    'taxonomy': HaLUrl(UrlData('api.taxonomies_taxonomy_resource', absolute=True,
                               url_data={'taxonomy': '__class__.__name__',
                                         'taxonomy_type': 'taxonomy_type'}),
                       required=False,),
})


taxonomy_item_post = ns.model('TaxonomyItemPOST', OrderedDict([
    ('name', fields.String(default='', required=True, title='Name')),
    ('description', fields.String(default='', required=False, nullable=True, title='Beschreibung', description='Nähere Erläuterung zu dem Taxonomieeintrag.')),
]))

taxonomy_item_put = ns.inherit('TaxonomyItemPUT', taxonomy_item_post, OrderedDict([
    ('id', fields.Integer(default=-1, required=True, example=1, readonly=True)),
]))

taxonomy_item_ref = ns.model('TaxonomyItemREF', OrderedDict([
    ('id', fields.Integer(default=-1, required=True, example=1, readonly=True)),
    ('name', fields.String(default='', required=False)),
    ('description', fields.String(default='', required=False, nullable=True)),
]))

taxonomy_item_get = ns.inherit('TaxonomyItemGET', taxonomy_item_put, OrderedDict([
    ('id', fields.Integer(default=-1, readonly=True, example=1)),
    ('_links', NestedFields(taxonomy_item_links)),
]))

# Use taxonomy_tree_item_get for marshalling:
# return marshal(test, taxonomy_tree_item_get), 200
taxonomy_tree_item_get = ns.inherit('TaxonomyTreeItemGET', taxonomy_item_get, OrderedDict())

taxonomy_tree_item_get['children'] = fields.List(fields.Nested(taxonomy_tree_item_get), default=[])


# Two tree models because of bugs in flask restplus:
# https://github.com/noirbizarre/flask-restplus/issues/280
# https://github.com/noirbizarre/flask-restplus/issues/293

# Use taxonomy_tree_item_get_json for documentation:
# @api.response(200, 'Success', taxonomy_tree_item_get_json)

taxonomy_tree_item_get_json = ns.schema_model('TaxonomyTreeItemGETJSON', {
    'allOf': [
        {
            '$ref': '#/definitions/{0}'.format(taxonomy_item_get.name),
        },
        {
            'properties': {
                'children': {
                    'type': 'array',
                    'items': {
                        '$ref': '#/definitions/TaxonomyTreeItemGETJSON'
                    }

test = 1
                }
            }
        }
    ]
})


class TaxonomyItems(fields.Raw):
    """Raw field for formatting taxonomy Items."""

    def format(self, items):
        if callable(items):
            items = items()
        if isinstance(items, list):
            return marshal(items, taxonomy_item_get)
        else:
            return marshal(items, taxonomy_tree_item_get)

    def schema(self):
        # does not work with swagger api!
        schema = {}
        listRef = '#/definitions/{0}'.format(taxonomy_item_get.name)
        treeRef = '#/definitions/{0}'.format(taxonomy_tree_item_get.name)
        schema['oneOf'] = [
            {'type': 'array', 'items': {'$ref': listRef}},
            {'$ref': treeRef},
        ]

        return schema


# models for taxonomies
taxonomy_links = ns.model('TaxonomyLinks', {
    'self': HaLUrl(UrlData('api.taxonomies_taxonomy_resource', absolute=True,
                           url_data={'taxonomy': '__name__', 'taxonomy_type': 'taxonomy_type'}),
                   required=False,),
    'collection': HaLUrl(UrlData('api.taxonomies_taxonomy_list_resource', absolute=True),
                         required=False),
})

taxonomy_model = ns.model('TaxonomyModel', {
    'name': fields.String(default='', required=True, attribute='__name__'),
    '_links': NestedFields(taxonomy_links),
    'taxonomy_type': fields.String(default='list', enum=['list', 'tree'], discriminator=True, readonly=True),
    'select_only_leafs': fields.Boolean(default=False, readonly=True, required=False),
    'select_multiple': fields.Boolean(default=False, readonly=True, required=False),
    'items': TaxonomyItems(required=False),
}, mask='{name,_links,taxonomy_type,select_only_leafs}')


list_taxonomy_model = ns.inherit('ListTaxonomy', taxonomy_model, {
    'items': fields.List(fields.Nested(taxonomy_item_get)),
})

tree_taxonomy_model = ns.inherit('TreeTaxonomyModel', taxonomy_model, {
    'items': fields.Nested(taxonomy_tree_item_get),
})

tree_taxonomy_model_json = ns.inherit('TreeTaxonomyModelJSON', taxonomy_model, {
    'items': fields.Nested(taxonomy_tree_item_get_json),
})

# models for list of taxonomies:
taxonomy_list_links = ns.inherit('TaxonomyListLinks', with_curies, {
    'self': HaLUrl(UrlData('api.taxonomies_taxonomy_list_resource', absolute=True), required=False),
    'taxonomy': HaLUrl(UrlData('api.taxonomies_taxonomy_list_resource', absolute=True,
                               templated=True, path_variables=['taxonomy']),
                       required=False),
})

taxonomy_list_resource = ns.model('TaxonomyList', {
    '_links': NestedFields(taxonomy_list_links),
    'taxonomies': fields.Nested(taxonomy_model, 'taxonomies', as_list=True),
})
