
import click
import sys
import csv
from glob import glob
from os import path
from inspect import getmembers, isclass
from typing import Dict

from .loadable_mixin import LoadableMixin
from ... import app


from .instruments import Instrument



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
    taxonomies = get_taxonomies()
    for file in files:
        name = path.splitext(path.basename(file))[0].upper()
        if name in taxonomies:
            if reload:
                click.echo('Clearing old taxonomie data for "{}"'.format(name))
                taxonomies[name].clear_all()
            click.echo('Loading taxonomie "{}"'.format(name))
            with open(file) as csv_file:
                dialect = csv.Sniffer().sniff(csv_file.read(1024))
                csv_file.seek(0)
                reader = csv.DictReader(csv_file, dialect=dialect)
                taxonomies[name].load(reader)
    click.echo('Test done.')


def get_taxonomies() -> Dict[str, LoadableMixin]:
    temp = {}
    for name, member in getmembers(sys.modules[__name__], isclass):
        if member is LoadableMixin:
            continue
        if issubclass(member, LoadableMixin):
            temp[name.upper()] = member
    return temp
