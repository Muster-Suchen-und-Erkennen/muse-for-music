
import click
import sys
import csv
from glob import glob
from os import path
from inspect import getmembers, isclass
from typing import Dict, TypeVar, Type

from .helper_classes import Taxonomy
from .. import DB_COMMAND_LOGGER
from ... import app


# Import taxonomy models:
from .instruments import Instrument, InstrumentierungEinbettungQualitaet, InstrumentierungEinbettungQuantitaet
from .chords import Akkord
from .misc import Anteil, AuftretenWerkausschnitt, AuftretenSatz, Frequenz
from .dissonance import Dissonanzen, Dissonanzgrad
from .dynamic import *
from .epoch import Epoche
from .form import FormaleFunktion, Formschema
from .gattung import GattungNineteenthCentury, Gattung
from .harmony import HarmonischeEntwicklung
from .notes import Grundton


T = TypeVar('T', bound=Taxonomy)


@app.cli.command('init_taxonomies')
@click.option('-r', '--reload', default=False, is_flag=True)
@click.argument('folder_path')
def init_taxonomies(reload, folder_path: str):
    """Init all taxonomies."""
    if not path.isdir(folder_path):
        click.echo('Please provide a path to a folder!')
        return
    folder_path = path.abspath(folder_path)
    click.echo('Scanning folder "{}"'.format(folder_path))
    files = glob(path.join(folder_path, '*.csv'))
    taxonomies = get_taxonomies()  # type: Dict[str, Type[T]]
    for file in files:
        name = path.splitext(path.basename(file))[0].upper()
        if name in taxonomies:
            tax = taxonomies[name]  # type: Type[T]
            if reload:
                click.echo('Clearing old taxonomy data for "{}"'.format(name))
                tax.clear_all(DB_COMMAND_LOGGER)
            click.echo('Loading taxonomy "{}"'.format(name))
            with open(file) as csv_file:
                dialect = csv.Sniffer().sniff(csv_file.read(1024))
                csv_file.seek(0)
                reader = csv.DictReader(csv_file, dialect=dialect)
                tax.load(reader, DB_COMMAND_LOGGER)
            click.echo('Finished processing taxonomy "{}"'.format(name))
        else:
            click.echo('No taxonomy table found for name "{}"'.format(name))
    click.echo('Finished processing all taxonomies.')


def get_taxonomies() -> Dict[str, Type[T]]:
    temp = {}
    for name, member in getmembers(sys.modules[__name__], isclass):
        if member is Taxonomy:
            continue
        if issubclass(member, Taxonomy):
            temp[name.upper()] = member
    return temp
