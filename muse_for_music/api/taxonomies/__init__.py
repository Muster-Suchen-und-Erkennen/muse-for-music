"""Module containing API Endpoints for Taxonomy Resources."""

from http import HTTPStatus
from typing import Dict, Type

from flask import current_app, request
from flask_jwt_extended import jwt_required
from flask_restx import Resource, marshal
from sqlalchemy.exc import IntegrityError

from ... import db
from ...models.taxonomies import Taxonomy, get_taxonomies
from ...user_api import RoleEnum, has_roles
from ...util import abort
from .. import api

ns = api.namespace("taxonomies", description="All Taxonomies.")

from .models import (  # noqa: E402
    list_taxonomy_model,
    taxonomy_item_get,
    taxonomy_item_post,
    taxonomy_list_resource,
    taxonomy_model,
    taxonomy_tree_item_get,
    taxonomy_tree_item_get_json,
    tree_taxonomy_model,
    tree_taxonomy_model_json,
)

taxonomies: Dict[str, Type[Taxonomy]] = get_taxonomies()


@ns.route("/")
class TaxonomyListResource(Resource):
    @ns.marshal_with(taxonomy_list_resource)
    @jwt_required()
    def get(self):
        taxonomy_list = list(taxonomies.values())
        return {"taxonomies": taxonomy_list}


def get_taxonomy(taxonomy_type: str, taxonomy_name: str) -> Type[Taxonomy]:
    taxonomy_name = taxonomy_name.upper()
    if taxonomy_name not in taxonomies:
        abort(HTTPStatus.NOT_FOUND, "The reqested Taxonomy could not be found.")
    taxonomy: Type[Taxonomy] = taxonomies[taxonomy_name]
    if taxonomy_type != taxonomy.taxonomy_type:
        abort(
            HTTPStatus.BAD_REQUEST,
            f"The type of the requested taxonomy does not match the requested taxonomy type. (requested type: {taxonomy_type}, taxonomy_type: {taxonomy.taxonomy_type})",
        )
    return taxonomy


@ns.route("/<string:taxonomy_type>/<string:taxonomy>/", doc=False)
class TaxonomyResource(Resource):
    @ns.marshal_with(taxonomy_model)
    @ns.response(HTTPStatus.BAD_REQUEST, "Mismatching taxonomy type.")
    @ns.response(HTTPStatus.NOT_FOUND, "Taxonomy not found.")
    @jwt_required()
    def get(self, taxonomy_type: str, taxonomy: str):
        return get_taxonomy(taxonomy_type, taxonomy)


@ns.route("/list/<string:taxonomy>/")
class ListTaxonomyResource(Resource):
    @ns.marshal_with(list_taxonomy_model)
    @ns.response(HTTPStatus.BAD_REQUEST, "Mismatching taxonomy type.")
    @ns.response(HTTPStatus.NOT_FOUND, "Taxonomy not found.")
    @jwt_required()
    def get(self, taxonomy: str):
        tax = get_taxonomy("list", taxonomy)
        if tax is None:
            abort(HTTPStatus.NOT_FOUND, 'Taxonomy "{}" not found.'.format(taxonomy))
        return tax

    @ns.doc(model=taxonomy_item_get, expect=[taxonomy_item_post], validate=True)
    @jwt_required()
    @has_roles([RoleEnum.taxonomy_editor])
    def post(self, taxonomy: str):
        tax = get_taxonomy("list", taxonomy)
        if tax is None:
            abort(HTTPStatus.NOT_FOUND, 'Taxonomy "{}" not found.'.format(taxonomy))
        item_data = request.get_json()
        item_data.pop("specifications", None)
        item = create_taxonomy_item(tax, item_data)
        db.session.add(item)
        db.session.commit()
        return marshal(item, taxonomy_item_get)


@ns.route("/tree/<string:taxonomy>/")
class TreeTaxonomyResource(Resource):
    @ns.response(HTTPStatus.OK, "success", tree_taxonomy_model_json)
    @ns.response(HTTPStatus.BAD_REQUEST, "Mismatching taxonomy type.")
    @ns.response(HTTPStatus.NOT_FOUND, "Taxonomy not found.")
    @jwt_required()
    def get(self, taxonomy: str):
        tax = get_taxonomy("tree", taxonomy)
        if tax is None:
            abort(HTTPStatus.NOT_FOUND, 'Taxonomy "{}" not found.'.format(taxonomy))
        return marshal(tax, tree_taxonomy_model)


def get_taxonomy_item(tax: Type[Taxonomy], item_id) -> Taxonomy:
    item = tax.get_by_id(item_id)
    if item is None:
        abort(HTTPStatus.NOT_FOUND, "Requested taxonomy item not found!")
    return item


def create_taxonomy_item(tax: Type[Taxonomy], new_values) -> Taxonomy:
    """Create an entry for a Taxonomy.

    Arguments:
        tax: Type[Taxonomy] -- The Taxonomy Class to create the item for.
        new_values: dict -- the new Taxonomy Item JSON Object.

    Returns:
        Taxonomy -- The created Taxonomy Item.
    """
    new_values.pop("specifications", None)  # TODO remove
    item = tax(**new_values)
    db.session.add(item)
    return item


def edit_taxonomy_item(item: Taxonomy, new_values: Dict):
    """Update a existing taxonomy Item.

    Arguments:
        item: Taxonomy -- The Item to update.
        new_values: Dict -- The new Values in the JSON Object
    """
    if "name" in new_values:
        if item.name == "root" and new_values["name"] != "root":
            abort(HTTPStatus.BAD_REQUEST, 'Can not change name of "root"!')
        if item.name == "na" and new_values["name"] != "na":
            abort(HTTPStatus.BAD_REQUEST, 'Can not change name of "na"!')
        item.name = new_values["name"]
    if "description" in new_values:
        item.description = new_values["description"]
    if "mapping" in new_values:
        print(item.mapping)
        item.mapping = new_values["mapping"]
        print(item.mapping)

    db.session.commit()


def delete_taxonomy_item(taxonomy: Type[Taxonomy], item_id: int):
    """Remove an item from a Taxonomy.

    Arguments:
        taxonomy: Type[Taxonomy] -- The Taxonomy Class to remove the item from.
        item_id: int -- The id of the Taxonomy Item to remove.
    """
    item = get_taxonomy_item(taxonomy, item_id)
    if item.name == "root":
        abort(HTTPStatus.BAD_REQUEST, 'Can not delete "root"!')
    if item.name == "na":
        abort(HTTPStatus.BAD_REQUEST, 'Can not delete "na"!')
    db.session.delete(item)
    db.session.commit()
    current_app.logger.info("Taxonomy item %s deleted.", item)


@ns.route("/<string:taxonomy_type>/<string:taxonomy>/<int:item_id>/", doc=False)
class TaxonomyItemResource(Resource):
    @ns.marshal_with(taxonomy_item_get)
    @ns.response(HTTPStatus.BAD_REQUEST, "Mismatching taxonomy type.")
    @ns.response(HTTPStatus.NOT_FOUND, "Taxonomy or Item not found.")
    @jwt_required()
    def get(self, taxonomy_type: str, taxonomy: str, item_id: int):
        tax = get_taxonomy(taxonomy_type, taxonomy)
        if tax is None:
            abort(HTTPStatus.NOT_FOUND, 'Taxonomy "{}" not found.'.format(taxonomy))
        return get_taxonomy_item(tax, item_id)

    @ns.response(HTTPStatus.BAD_REQUEST, "Mismatching taxonomy type.")
    @ns.response(HTTPStatus.NOT_FOUND, "Taxonomy or Item not found.")
    @ns.doc(model=taxonomy_item_get, expect=[taxonomy_item_post], validate=True)
    @jwt_required()
    @has_roles([RoleEnum.taxonomy_editor])
    def put(self, taxonomy_type: str, taxonomy: str, item_id: int):
        tax = get_taxonomy(taxonomy_type, taxonomy)
        if tax is None:
            abort(HTTPStatus.NOT_FOUND, 'Taxonomy "{}" not found.'.format(taxonomy))
        item = get_taxonomy_item(tax, item_id)
        item_data = request.get_json()
        item_data.pop("specifications", None)
        edit_taxonomy_item(item, item_data)
        return marshal(item, taxonomy_item_get)

    @ns.response(HTTPStatus.BAD_REQUEST, "Mismatching taxonomy type.")
    @ns.response(HTTPStatus.NOT_FOUND, "Taxonomy or Item not found.")
    @jwt_required()
    @has_roles([RoleEnum.taxonomy_editor])
    def delete(self, taxonomy_type: str, taxonomy: str, item_id: int):
        tax = get_taxonomy(taxonomy_type, taxonomy)
        if tax is None:
            abort(HTTPStatus.NOT_FOUND, 'Taxonomy "{}" not found.'.format(taxonomy))
        try:
            delete_taxonomy_item(tax, item_id)
        except IntegrityError:
            db.session.rollback()
            abort(HTTPStatus.BAD_REQUEST, "Taxonomy item is still in use!")


@ns.route("/list/<string:taxonomy>/<int:item_id>/")
class ListTaxonomyItemResource(Resource):
    @ns.marshal_with(taxonomy_item_get)
    @ns.response(HTTPStatus.BAD_REQUEST, "Mismatching taxonomy type.")
    @ns.response(HTTPStatus.NOT_FOUND, "Taxonomy or Item not found.")
    @jwt_required()
    def get(self, taxonomy: str, item_id: int):
        tax = get_taxonomy("list", taxonomy)
        if tax is None:
            abort(HTTPStatus.NOT_FOUND, 'Taxonomy "{}" not found.'.format(taxonomy))
        return get_taxonomy_item(tax, item_id)

    @ns.response(HTTPStatus.BAD_REQUEST, "Mismatching taxonomy type.")
    @ns.response(HTTPStatus.NOT_FOUND, "Taxonomy or Item not found.")
    @ns.doc(model=taxonomy_item_get, expect=[taxonomy_item_post], validate=True)
    @jwt_required()
    @has_roles([RoleEnum.taxonomy_editor])
    def put(self, taxonomy: str, item_id: int):
        tax = get_taxonomy("list", taxonomy)
        if tax is None:
            abort(HTTPStatus.NOT_FOUND, 'Taxonomy "{}" not found.'.format(taxonomy))
        item = get_taxonomy_item(tax, item_id)
        item_data = request.get_json()
        item_data.pop("specifications", None)
        edit_taxonomy_item(item, item_data)
        return marshal(item, taxonomy_item_get)

    @ns.response(HTTPStatus.BAD_REQUEST, "Mismatching taxonomy type.")
    @ns.response(HTTPStatus.NOT_FOUND, "Taxonomy or Item not found.")
    @jwt_required()
    @has_roles([RoleEnum.taxonomy_editor])
    def delete(self, taxonomy: str, item_id: int):
        tax = get_taxonomy("list", taxonomy)
        if tax is None:
            abort(HTTPStatus.NOT_FOUND, 'Taxonomy "{}" not found.'.format(taxonomy))
        try:
            delete_taxonomy_item(tax, item_id)
        except IntegrityError:
            db.session.rollback()
            abort(HTTPStatus.BAD_REQUEST, "Taxonomy item is still in use!")


@ns.route("/tree/<string:taxonomy>/<int:item_id>/")
class TreeTaxonomyItemResource(Resource):
    @ns.response(HTTPStatus.OK, "success", model=taxonomy_tree_item_get_json)
    @ns.response(HTTPStatus.BAD_REQUEST, "Mismatching taxonomy type.")
    @ns.response(HTTPStatus.NOT_FOUND, "Taxonomy or Item not found.")
    @jwt_required()
    def get(self, taxonomy: str, item_id: int):
        tax = get_taxonomy("tree", taxonomy)
        if tax is None:
            abort(HTTPStatus.NOT_FOUND, 'Taxonomy "{}" not found.'.format(taxonomy))
        return marshal(get_taxonomy_item(tax, item_id), taxonomy_tree_item_get)

    @ns.doc(
        model=taxonomy_tree_item_get_json, expect=[taxonomy_item_post], validate=True
    )
    @jwt_required()
    @has_roles([RoleEnum.taxonomy_editor])
    def post(self, taxonomy: str, item_id: int):
        tax = get_taxonomy("tree", taxonomy)
        if tax is None:
            abort(HTTPStatus.NOT_FOUND, 'Taxonomy "{}" not found.'.format(taxonomy))
        new_item = request.get_json()
        new_item.pop("specifications", None)
        if new_item["name"] == "root":
            abort(HTTPStatus.BAD_REQUEST, 'Name "root" is forbidden!')
        new_item["parent"] = get_taxonomy_item(tax, item_id)
        item = create_taxonomy_item(tax, new_item)
        db.session.add(item)
        db.session.commit()
        return marshal(item, taxonomy_tree_item_get)

    @ns.response(HTTPStatus.BAD_REQUEST, "Mismatching taxonomy type.")
    @ns.response(HTTPStatus.NOT_FOUND, "Taxonomy or Item not found.")
    @ns.doc(
        model=taxonomy_tree_item_get_json, expect=[taxonomy_item_post], validate=True
    )
    @jwt_required()
    @has_roles([RoleEnum.taxonomy_editor])
    def put(self, taxonomy: str, item_id: int):
        tax = get_taxonomy("tree", taxonomy)
        if tax is None:
            abort(HTTPStatus.NOT_FOUND, 'Taxonomy "{}" not found.'.format(taxonomy))
        item = get_taxonomy_item(tax, item_id)
        item_data = request.get_json()
        item_data.pop("specifications", None)
        edit_taxonomy_item(item, item_data)
        return marshal(item, taxonomy_tree_item_get)

    @ns.response(HTTPStatus.BAD_REQUEST, "Mismatching taxonomy type.")
    @ns.response(HTTPStatus.NOT_FOUND, "Taxonomy or Item not found.")
    @jwt_required()
    @has_roles([RoleEnum.taxonomy_editor])
    def delete(self, taxonomy: str, item_id: int):
        tax = get_taxonomy("tree", taxonomy)
        if tax is None:
            abort(HTTPStatus.NOT_FOUND, 'Taxonomy "{}" not found.'.format(taxonomy))
        try:
            delete_taxonomy_item(tax, item_id)
        except IntegrityError:
            db.session.rollback()
            abort(
                HTTPStatus.BAD_REQUEST,
                "The taxonomy item or one of its children is still in use!",
            )
