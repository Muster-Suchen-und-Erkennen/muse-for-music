from flask import request
from flask_restplus import Resource, marshal, abort

from ...models.taxonomies import get_taxonomies, T
from .. import api
from ... import app, db

from typing import TypeVar, Dict, Type, cast

ns = api.namespace('taxonomies', description='All Taxonomies.')

from .models import taxonomy_list_resource, taxonomy_model, list_taxonomy_model, \
                    tree_taxonomy_model, tree_taxonomy_model_json, \
                    taxonomy_item_get, taxonomy_tree_item_get, \
                    taxonomy_tree_item_get_json, taxonomy_item_post


taxonomies = get_taxonomies()  # type:Dict[str, Type[T]]


@ns.route('/')
class TaxonomyListResource(Resource):

    @ns.marshal_with(taxonomy_list_resource)
    def get(self):
        taxonomy_list = list(taxonomies.values())
        return{'taxonomies': taxonomy_list}


def get_taxonomy(taxonomy_type: str, taxonomy_name: str) -> Type[T]:
        taxonomy_name = taxonomy_name.upper()
        if taxonomy_name not in taxonomies:
            abort(404, 'The reqested Taxonomy could not be found.')
        taxonomy = taxonomies[taxonomy_name]  # type: Type[T]
        if taxonomy_type != taxonomy.taxonomy_type:
            abort(400, 'The type of the requested taxonomy does not match the requested taxonomy type. (requested type: {}, taxonomy_type: {})'
                  .format(taxonomy_type, taxonomy.taxonomy_type))
        return cast(Type[T], taxonomy)


@ns.route('/<string:taxonomy_type>/<string:taxonomy>', doc=False)
class TaxonomyResource(Resource):

    @ns.marshal_with(taxonomy_model)
    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy not found.')
    def get(self, taxonomy_type: str, taxonomy: str):
        return get_taxonomy(taxonomy_type, taxonomy)


@ns.route('/list/<string:taxonomy>')
class ListTaxonomyResource(Resource):

    @ns.marshal_with(list_taxonomy_model)
    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy not found.')
    def get(self, taxonomy: str):
        return get_taxonomy('list', taxonomy)

    @ns.doc(model=taxonomy_item_get, body=taxonomy_item_post, vaidate=True)
    def post(self, taxonomy: str):
        tax = get_taxonomy('list', taxonomy)
        item = create_taxonomy_item(tax, request.get_json())
        db.session.add(item)
        db.session.commit()
        return marshal(item, taxonomy_item_get)


@ns.route('/tree/<string:taxonomy>')
class TreeTaxonomyResource(Resource):

    @ns.response('200', 'success', tree_taxonomy_model_json)
    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy not found.')
    def get(self, taxonomy: str):
        return marshal(get_taxonomy('tree', taxonomy), tree_taxonomy_model)


def get_taxonomy_item(tax: Type[T], item_id) -> T:
    item = tax.get_by_id(item_id)
    if item is None:
        abort(404, 'Requested taxonomy item not found!')
    return item


def create_taxonomy_item(tax: Type[T], new_values) -> T:
    item = tax(**new_values)
    db.session.add(item)
    return item


def edit_taxonomy_item(item: T, new_values: Dict):
    if 'name' in new_values:
        item.name = new_values['name']
    if 'description' in new_values:
        item.description = new_values['description']
    db.session.commit()


def delete_taxonomy_item(taxonomy: Type[T], item_id: int):
    item = get_taxonomy_item(taxonomy, item_id)
    db.session.delete(item)
    db.session.commit()
    app.logger.info('Taxonomy item %s deleted.', item)


@ns.route('/<string:taxonomy_type>/<string:taxonomy>/<int:item_id>', doc=False)
class TaxonomyItemResource(Resource):

    @ns.marshal_with(taxonomy_item_get)
    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy or Item not found.')
    def get(self, taxonomy_type: str, taxonomy: str, item_id: int):
        tax = get_taxonomy(taxonomy_type, taxonomy)
        return get_taxonomy_item(tax, item_id)

    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy or Item not found.')
    @ns.doc(model=taxonomy_item_get, body=taxonomy_item_post, vaidate=True)
    def put(self, taxonomy_type: str, taxonomy: str, item_id: int):
        tax = get_taxonomy(taxonomy_type, taxonomy)
        item = get_taxonomy_item(tax, item_id)
        edit_taxonomy_item(item, request.get_json())
        return marshal(item, taxonomy_item_get)

    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy or Item not found.')
    def delete(self, taxonomy_type: str, taxonomy: str, item_id: int):
        tax = get_taxonomy(taxonomy_type, taxonomy)
        delete_taxonomy_item(tax, item_id)


@ns.route('/list/<string:taxonomy>/<int:item_id>')
class ListTaxonomyItemResource(Resource):

    @ns.marshal_with(taxonomy_item_get)
    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy or Item not found.')
    def get(self, taxonomy: str, item_id: int):
        tax = get_taxonomy('list', taxonomy)
        return get_taxonomy_item(tax, item_id)

    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy or Item not found.')
    @ns.doc(model=taxonomy_item_get, body=taxonomy_item_post, vaidate=True)
    def put(self, taxonomy: str, item_id: int):
        tax = get_taxonomy('list', taxonomy)
        item = get_taxonomy_item(tax, item_id)
        edit_taxonomy_item(item, request.get_json())
        return marshal(item, taxonomy_item_get)

    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy or Item not found.')
    def delete(self, taxonomy: str, item_id: int):
        tax = get_taxonomy('list', taxonomy)
        delete_taxonomy_item(tax, item_id)


@ns.route('/tree/<string:taxonomy>/<int:item_id>')
class TreeTaxonomyItemResource(Resource):

    @ns.response(200, 'success', model=taxonomy_tree_item_get_json)
    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy or Item not found.')
    def get(self, taxonomy: str, item_id: int):
        tax = get_taxonomy('tree', taxonomy)
        return marshal(get_taxonomy_item(tax, item_id), taxonomy_tree_item_get)

    @ns.doc(model=taxonomy_tree_item_get_json, body=taxonomy_item_post, vaidate=True)
    def post(self, taxonomy: str, item_id: int):
        tax = get_taxonomy('tree', taxonomy)
        new_item = request.get_json()
        new_item['parent'] = get_taxonomy_item(tax, item_id)
        item = create_taxonomy_item(tax, new_item)
        db.session.add(item)
        db.session.commit()
        return marshal(item, taxonomy_tree_item_get)

    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy or Item not found.')
    @ns.doc(model=taxonomy_tree_item_get_json, body=taxonomy_item_post, vaidate=True)
    def put(self, taxonomy: str, item_id: int):
        tax = get_taxonomy('tree', taxonomy)
        item = get_taxonomy_item(tax, item_id)
        edit_taxonomy_item(item, request.get_json())
        return marshal(item, taxonomy_tree_item_get)

    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy or Item not found.')
    def delete(self, taxonomy: str, item_id: int):
        tax = get_taxonomy('tree', taxonomy)
        delete_taxonomy_item(tax, item_id)
