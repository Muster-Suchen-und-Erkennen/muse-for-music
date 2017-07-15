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


from flask_restplus import fields
from . import ns


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
    'name': fields.String
})

tree_model['children'] = fields.List(fields.Nested(tree_model), default=[])


# model for list items:

list_item_model = ns.model('ListItemModel', {
    'name': fields.String
})
