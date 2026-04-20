import csv
import sys
from glob import glob
from inspect import getmembers, isclass
from os import makedirs, path
from typing import Dict, Type

import click
from flask import current_app
from flask.cli import with_appcontext
from sqlalchemy.sql import delete, select
from sqlalchemy.sql.functions import count

from .. import DB_CLI, DB_COMMAND_LOGGER, db

# Import taxonomy models:
from .ambitus import *  # noqa
from .chords import *  # noqa
from .citation import *  # noqa
from .composition import *  # noqa
from .dissonance import *  # noqa
from .dynamic import *  # noqa
from .epoch import *  # noqa
from .form import *  # noqa
from .gattung import *  # noqa
from .harmonics import *  # noqa
from .helper_classes import ListTaxonomy, Taxonomy, TreeTaxonomy  # noqa
from .instruments import *  # noqa
from .melody import *  # noqa
from .misc import *  # noqa
from .notes import *  # noqa
from .rendition import *  # noqa
from .rhythm import *  # noqa
from .satz import *  # noqa
from .specifications import *  # noqa
from .tempo import *  # noqa
from .voices import *  # noqa


def generate_na_elements(output: bool = False):
    """Generate all missing "na" elements."""
    taxonomies = get_taxonomies()
    for name, taxonomy in taxonomies.items():
        try:
            count_q = select(count(taxonomy.id))
            item_count = db.session.execute(count_q).scalar()
            if item_count == 0:
                if output:
                    click.echo(f'Skip NA item for "{name}" because it has no items.')
                continue  # skip taxonomies without any entry
        except Exception as err:
            click.echo(f'Skip NA item for "{name}" because of an error.', err)
            continue  # skip non existing taxonomies
        na = taxonomy.not_applicable_item()
        if na is None:
            if output:
                click.echo(f'Add NA item for "{name}".')
            db.session.add(taxonomy(name="na", description=None))
        else:
            if output:
                click.echo(f'"{name}" already has NA item.')
    db.session.commit()


def remove_unreachable_elements(output: bool = False):
    taxonomies = get_taxonomies()
    for name, taxonomy in taxonomies.items():
        if not issubclass(taxonomy, TreeTaxonomy):
            continue
        root = taxonomy.get_root()
        all_item_ids_q = select(taxonomy.id).where(taxonomy.name != "na")
        all_item_ids = set(db.session.execute(all_item_ids_q).scalars().all())
        stack = [root]
        while stack:
            current = stack.pop()
            assert current is not None
            all_item_ids.discard(current.id)
            stack.extend(current.children)
        if all_item_ids:
            if output:
                click.echo(
                    f'Taxonomy "{name}" has {len(all_item_ids)} items that are not connected to the tree. Disconnected items: {all_item_ids}'
                )
            del_q = delete(taxonomy).where(taxonomy.id.in_(all_item_ids))
            db.session.execute(del_q)
    db.session.commit()


@DB_CLI.cli.command("init_taxonomies")
@click.option("-r", "--reload", default=False, is_flag=True)
@click.argument("folder_path")
@with_appcontext
def init_taxonomies(reload, folder_path: str):
    """Init all taxonomies."""
    if not path.isdir(folder_path):
        click.echo("Please provide a path to a folder!")
        return
    if reload and current_app.config.get("DEBUG", False):
        current_app.config["SQLITE_FOREIGN_KEYS"] = False
    folder_path = path.abspath(folder_path)
    click.echo('Scanning folder "{}"'.format(folder_path))
    files = glob(path.join(folder_path, "*.csv"))
    taxonomies: dict[str, Type[Taxonomy]] = get_taxonomies()
    unmatched_csv_files = []
    for file in files:
        name = path.splitext(path.basename(file))[0].upper()
        if name in taxonomies:
            tax: Type[Taxonomy] = taxonomies[name]
            if reload:
                click.echo('Clearing old taxonomy data for "{}"'.format(name))
                tax.clear_all(DB_COMMAND_LOGGER)
            click.echo('Loading taxonomy "{}"'.format(name))
            with open(file) as csv_file:
                dialect = csv.Sniffer().sniff(csv_file.readline())
                csv_file.seek(0)
                reader = csv.DictReader(csv_file, dialect=dialect)
                tax.load(reader, DB_COMMAND_LOGGER)
            click.echo('Finished processing taxonomy "{}"'.format(name))
        else:
            unmatched_csv_files.append(name)
    click.echo('Making sure every taxonomy has a "not applicable" element.')
    generate_na_elements(output=True)
    remove_unreachable_elements(output=True)
    click.echo("Finished processing all taxonomies.")
    for name in unmatched_csv_files:
        click.echo('No taxonomy table found for name "{}"'.format(name))


@DB_CLI.cli.command("add_na_elements")
@with_appcontext
def add_na_elements():
    """Add all missing "na" elements."""
    click.echo('Making sure every taxonomy has a "not applicable" element.')
    generate_na_elements(output=True)
    click.echo("Finished processing all taxonomies.")


@DB_CLI.cli.command("clean_disconnected_elements")
@with_appcontext
def clean_disconnected_elements():
    click.echo("Making sure tree taxonomies have no disconnected elements.")
    remove_unreachable_elements(output=True)
    click.echo("Finished removing all disconnected elements.")


@DB_CLI.cli.command("export_taxonomies")
@click.argument("folder_path")
@with_appcontext
def save_taxonomies(folder_path: str):
    """Export all taxonomies."""
    folder_path = path.abspath(folder_path)
    if path.isfile(folder_path):
        click.echo("Please provide a path to a folder!")
        return
    makedirs(folder_path, exist_ok=True)
    taxonomies: Dict[str, Type[Taxonomy]] = get_taxonomies()
    click.echo('Exporting taxonomies into folder "{}"'.format(folder_path))
    for name, taxonomy in taxonomies.items():
        filepath = path.join(folder_path, taxonomy.__name__ + ".csv")
        click.echo('Preparing taxonomy "{}" for export'.format(name))
        with open(filepath, mode="w") as csv_file:
            writer = csv.DictWriter(
                csv_file, ["name", "parent", "description"], dialect=csv.excel
            )
            taxonomy.save(writer, DB_COMMAND_LOGGER)
        click.echo('Finished exporting taxonomy "{}"'.format(name))
    click.echo("Finished exporting all taxonomies.")


def get_taxonomies() -> Dict[str, Type[Taxonomy]]:
    temp = {}
    for name, member in getmembers(sys.modules[__name__], isclass):
        if member is Taxonomy or member is TreeTaxonomy or member is ListTaxonomy:
            continue
        if issubclass(member, Taxonomy):
            temp[name.upper()] = member
    return temp
