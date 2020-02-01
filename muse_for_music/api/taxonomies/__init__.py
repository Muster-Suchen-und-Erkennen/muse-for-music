"""Module containing API Endpoints for Taxonomy Resources."""

from flask import request, current_app
from flask_restplus import Resource, marshal, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from ...models.taxonomies import get_taxonomies, T
from .. import api
from ... import db
from ...user_api import has_roles, RoleEnum

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
    @jwt_required
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


@ns.route('/<string:taxonomy_type>/<string:taxonomy>/', doc=False)
class TaxonomyResource(Resource):

    @ns.marshal_with(taxonomy_model)
    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy not found.')
    @jwt_required
    def get(self, taxonomy_type: str, taxonomy: str):
        return get_taxonomy(taxonomy_type, taxonomy)


@ns.route('/list/<string:taxonomy>/')
class ListTaxonomyResource(Resource):

    @ns.marshal_with(list_taxonomy_model)
    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy not found.')
    @jwt_required
    def get(self, taxonomy: str):
        tax = get_taxonomy('list', taxonomy)
        if tax is None:
            abort(404, 'Taxonomy "{}" not found.'.format(taxonomy))
        return tax

    @ns.doc(model=taxonomy_item_get, body=taxonomy_item_post, vaidate=True)
    @jwt_required
    @has_roles([RoleEnum.taxonomy_editor])
    def post(self, taxonomy: str):
        tax = get_taxonomy('list', taxonomy)
        if tax is None:
            abort(404, 'Taxonomy "{}" not found.'.format(taxonomy))
        item = create_taxonomy_item(tax, request.get_json())
        db.session.add(item)
        db.session.commit()
        return marshal(item, taxonomy_item_get)


@ns.route('/tree/<string:taxonomy>/')
class TreeTaxonomyResource(Resource):

    @ns.response('200', 'success', tree_taxonomy_model_json)
    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy not found.')
    @jwt_required
    def get(self, taxonomy: str):
        tax = get_taxonomy('tree', taxonomy)
        if tax is None:
            abort(404, 'Taxonomy "{}" not found.'.format(taxonomy))
        return marshal(tax, tree_taxonomy_model)


def get_taxonomy_item(tax: Type[T], item_id) -> T:
    item = tax.get_by_id(item_id)
    if item is None:
        abort(404, 'Requested taxonomy item not found!')
    return item


def create_taxonomy_item(tax: Type[T], new_values) -> T:
    """Create an entry for a Taxonomy.

    Arguments:
        tax: Type[T] -- The Taxonomy Class to create the item for.
        new_values: dict -- the new Taxonomy Item JSON Object.

    Returns:
        T -- The created Taxonomy Item.
    """
    item = tax(**new_values)
    db.session.add(item)
    return item


def edit_taxonomy_item(item: T, new_values: Dict):
    """Update a existing taxonomy Item.

    Arguments:
        item: T -- The Item to update.
        new_values: Dict -- The new Values in the JSON Object
    """
    if 'name' in new_values:
        if item.name == 'root' and new_values['name'] != 'root':
            abort(400, 'Can not change name of "root"!')
        if item.name == 'na' and new_values['name'] != 'na':
            abort(400, 'Can not change name of "na"!')
        item.name = new_values['name']
    if 'description' in new_values:
        item.description = new_values['description']
    db.session.commit()


def delete_taxonomy_item(taxonomy: Type[T], item_id: int):
    """Remove an item from a Taxonomy.

    Arguments:
        taxonomy: Type[T] -- The Taxonomy Class to remove the item from.
        item_id: int -- The id of the Taxonomy Item to remove.
    """
    item = get_taxonomy_item(taxonomy, item_id)
    if item.name == 'root':
        abort(400, 'Can not delete "root"!')
    if item.name == 'na':
        abort(400, 'Can not delete "na"!')
    db.session.delete(item)
    db.session.commit()
    current_app.logger.info('Taxonomy item %s deleted.', item)


@ns.route('/<string:taxonomy_type>/<string:taxonomy>/<int:item_id>/', doc=False)
class TaxonomyItemResource(Resource):

    @ns.marshal_with(taxonomy_item_get)
    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy or Item not found.')
    @jwt_required
    def get(self, taxonomy_type: str, taxonomy: str, item_id: int):
        tax = get_taxonomy(taxonomy_type, taxonomy)
        if tax is None:
            abort(404, 'Taxonomy "{}" not found.'.format(taxonomy))
        return get_taxonomy_item(tax, item_id)

    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy or Item not found.')
    @ns.doc(model=taxonomy_item_get, body=taxonomy_item_post, vaidate=True)
    @jwt_required
    @has_roles([RoleEnum.taxonomy_editor])
    def put(self, taxonomy_type: str, taxonomy: str, item_id: int):
        tax = get_taxonomy(taxonomy_type, taxonomy)
        if tax is None:
            abort(404, 'Taxonomy "{}" not found.'.format(taxonomy))
        item = get_taxonomy_item(tax, item_id)
        edit_taxonomy_item(item, request.get_json())
        return marshal(item, taxonomy_item_get)

    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy or Item not found.')
    @jwt_required
    @has_roles([RoleEnum.taxonomy_editor])
    def delete(self, taxonomy_type: str, taxonomy: str, item_id: int):
        tax = get_taxonomy(taxonomy_type, taxonomy)
        if tax is None:
            abort(404, 'Taxonomy "{}" not found.'.format(taxonomy))
        try:
            delete_taxonomy_item(tax, item_id)
        except IntegrityError:
            db.session.rollback()
            abort(400, 'Taxonomy item is still in use!')


@ns.route('/list/<string:taxonomy>/<int:item_id>/')
class ListTaxonomyItemResource(Resource):

    @ns.marshal_with(taxonomy_item_get)
    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy or Item not found.')
    @jwt_required
    def get(self, taxonomy: str, item_id: int):
        tax = get_taxonomy('list', taxonomy)
        if tax is None:
            abort(404, 'Taxonomy "{}" not found.'.format(taxonomy))
        return get_taxonomy_item(tax, item_id)

    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy or Item not found.')
    @ns.doc(model=taxonomy_item_get, body=taxonomy_item_post, vaidate=True)
    @jwt_required
    @has_roles([RoleEnum.taxonomy_editor])
    def put(self, taxonomy: str, item_id: int):
        tax = get_taxonomy('list', taxonomy)
        if tax is None:
            abort(404, 'Taxonomy "{}" not found.'.format(taxonomy))
        item = get_taxonomy_item(tax, item_id)
        edit_taxonomy_item(item, request.get_json())
        return marshal(item, taxonomy_item_get)

    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy or Item not found.')
    @jwt_required
    @has_roles([RoleEnum.taxonomy_editor])
    def delete(self, taxonomy: str, item_id: int):
        tax = get_taxonomy('list', taxonomy)
        if tax is None:
            abort(404, 'Taxonomy "{}" not found.'.format(taxonomy))
        try:
            delete_taxonomy_item(tax, item_id)
        except IntegrityError:
            db.session.rollback()
            abort(400, 'Taxonomy item is still in use!')


@ns.route('/tree/<string:taxonomy>/<int:item_id>/')
class TreeTaxonomyItemResource(Resource):

    @ns.response(200, 'success', model=taxonomy_tree_item_get_json)
    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy or Item not found.')
    @jwt_required
    def get(self, taxonomy: str, item_id: int):
        tax = get_taxonomy('tree', taxonomy)
        if tax is None:
            abort(404, 'Taxonomy "{}" not found.'.format(taxonomy))
        return marshal(get_taxonomy_item(tax, item_id), taxonomy_tree_item_get)

    @ns.doc(model=taxonomy_tree_item_get_json, body=taxonomy_item_post, vaidate=True)
    @jwt_required
    @has_roles([RoleEnum.taxonomy_editor])
    def post(self, taxonomy: str, item_id: int):
        tax = get_taxonomy('tree', taxonomy)
        if tax is None:
            abort(404, 'Taxonomy "{}" not found.'.format(taxonomy))
        new_item = request.get_json()
        if new_item['name'] == 'root':
            abort(400, 'Name "root" is forbidden!')
        new_item['parent'] = get_taxonomy_item(tax, item_id)
        item = create_taxonomy_item(tax, new_item)
        db.session.add(item)
        db.session.commit()
        return marshal(item, taxonomy_tree_item_get)

    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy or Item not found.')
    @ns.doc(model=taxonomy_tree_item_get_json, body=taxonomy_item_post, vaidate=True)
    @jwt_required
    @has_roles([RoleEnum.taxonomy_editor])
    def put(self, taxonomy: str, item_id: int):
        tax = get_taxonomy('tree', taxonomy)
        if tax is None:
            abort(404, 'Taxonomy "{}" not found.'.format(taxonomy))
        item = get_taxonomy_item(tax, item_id)
        edit_taxonomy_item(item, request.get_json())
        return marshal(item, taxonomy_tree_item_get)

    @ns.response(400, 'Mismatching taxonomy type.')
    @ns.response(404, 'Taxonomy or Item not found.')
    @jwt_required
    @has_roles([RoleEnum.taxonomy_editor])
    def delete(self, taxonomy: str, item_id: int):
        tax = get_taxonomy('tree', taxonomy)
        if tax is None:
            abort(404, 'Taxonomy "{}" not found.'.format(taxonomy))
        try:
            delete_taxonomy_item(tax, item_id)
        except IntegrityError:
            db.session.rollback()
            abort(400, 'The taxonomy item or one of its children is still in use!')
