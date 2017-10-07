from flask import render_template, url_for, abort
from . import debug_blueprint
from ..models.taxonomies import get_taxonomies
from ..models.taxonomies.helper_classes import ListTaxonomy


@debug_blueprint.route('/taxonomies')
def taxonomies():
    return render_template('debug/taxonomies/all.html',
                           title='muse4music – Taxonomies',
                           taxonomies=get_taxonomies().keys())


@debug_blueprint.route('/taxonomies/<string:taxonomy>')
def view_taxonomy(taxonomy: str):
    tax = get_taxonomies().get(taxonomy, None)
    if tax is None:
        abort(404)
    if issubclass(tax, ListTaxonomy):
        template = 'debug/taxonomies/list.html'
        content = tax.get_all()
    else:
        template = 'debug/taxonomies/tree.html'
        content = (tax.get_root(), )
    return render_template(template,
                           title='muse4music – Taxonomy: {}'.format(taxonomy),
                           taxonomy=taxonomy,
                           content=content)
