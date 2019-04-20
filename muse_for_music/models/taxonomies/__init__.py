
import click
import sys
import csv
from glob import glob
from os import path, makedirs
from inspect import getmembers, isclass
from typing import Dict, TypeVar, Type

from .helper_classes import Taxonomy
from .. import DB_COMMAND_LOGGER
from ... import app


# Import taxonomy models:
from .ambitus import *
from .instruments import *
from .chords import *
from .misc import *
from .dissonance import *
from .dynamic import *
from .epoch import *
from .form import *
from .gattung import *
from .harmonics import *
from .notes import *
from .melody import *
from .rhythm import *
from .satz import *
from .tempo import *
from .composition import *
from .citation import *
from .voices import *
from .rendition import *


T = TypeVar('T', bound=Taxonomy)


@app.cli.command('init_taxonomies')
@click.option('-r', '--reload', default=False, is_flag=True)
@click.argument('folder_path')
def init_taxonomies(reload, folder_path: str):
    """Init all taxonomies."""
    if not path.isdir(folder_path):
        click.echo('Please provide a path to a folder!')
        return
    if reload and app.config.get('DEBUG', False):
        app.config['SQLITE_FOREIGN_KEYS'] = False
    folder_path = path.abspath(folder_path)
    click.echo('Scanning folder "{}"'.format(folder_path))
    files = glob(path.join(folder_path, '*.csv'))
    taxonomies = get_taxonomies()  # type: Dict[str, Type[T]]
    unmatched_csv_files = []
    for file in files:
        name = path.splitext(path.basename(file))[0].upper()
        if name in taxonomies:
            tax = taxonomies[name]  # type: Type[T]
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
    click.echo('Finished processing all taxonomies.')
    for name in unmatched_csv_files:
        click.echo('No taxonomy table found for name "{}"'.format(name))

@app.cli.command('export_taxonomies')
@click.argument('folder_path')
def save_taxonomies(folder_path: str):
    """Export all taxonomies."""
    folder_path = path.abspath(folder_path)
    if path.isfile(folder_path):
        click.echo('Please provide a path to a folder!')
        return
    makedirs(folder_path, exist_ok=True)
    taxonomies = get_taxonomies()  # type: Dict[str, Type[T]]
    click.echo('Exporting taxonomies into folder "{}"'.format(folder_path))
    for name, taxonomy in taxonomies.items():
        filepath = path.join(folder_path, taxonomy.__name__ + '.csv')
        click.echo('Preparing taxonomy "{}" for export'.format(name))
        with open(filepath, mode='w') as csv_file:
            writer = csv.DictWriter(csv_file, ['name', 'parent', 'description'], dialect=csv.excel)
            taxonomy.save(writer, DB_COMMAND_LOGGER)
        click.echo('Finished exporting taxonomy "{}"'.format(name))
    click.echo('Finished exporting all taxonomies.')



def get_taxonomies() -> Dict[str, Type[T]]:
    temp = {}
    for name, member in getmembers(sys.modules[__name__], isclass):
        if member is Taxonomy:
            continue
        if issubclass(member, Taxonomy):
            temp[name.upper()] = member
    return temp
