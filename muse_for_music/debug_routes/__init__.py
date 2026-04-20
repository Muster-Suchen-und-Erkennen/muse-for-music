"""
Module containing Debug Methods and sites.

This Module should only be loaded in debug Mode.
"""

from flask import Blueprint, Flask, render_template

debug_blueprint = Blueprint(
    "debug_routes", __name__, template_folder="templates", static_folder="static"
)

from . import debug_db_models, debug_taxonomies, routes  # noqa


@debug_blueprint.route("/")
@debug_blueprint.route("/index")
def index():
    return render_template("debug/index.html", title="muse4music – Debug")


def register_debug_routes(app: Flask):
    if not app.config["DEBUG"]:
        raise Warning("This Module should only be loaded if DEBUG mode is active!")
    app.register_blueprint(debug_blueprint, url_prefix="/debug")
