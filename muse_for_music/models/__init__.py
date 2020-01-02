from logging import Logger, StreamHandler, Formatter, getLogger, DEBUG
from sys import stdout
from flask import Flask
from flask.cli import with_appcontext
import click


from .. import db
from .users import User, UserRole, RoleEnum

DB_COMMAND_LOGGER = getLogger('flask.app.db')  # type: Logger

formatter = Formatter(fmt='[%(levelname)s] [%(name)-16s] %(message)s')

handler = StreamHandler(stream=stdout)

handler.setFormatter(formatter)

DB_COMMAND_LOGGER.addHandler(handler)

DB_COMMAND_LOGGER.setLevel(DEBUG)

from . import taxonomies
from . import data
from .data.people import Person
from .data.history import History, MethodEnum


@click.command('create_db')
@with_appcontext
def create_db():
    """Create all db tables."""
    create_db_function()
    click.echo('Database created.')


def create_db_function():
    db.create_all()
    DB_COMMAND_LOGGER.info('Database created.')


@click.command('drop_db')
@with_appcontext
def drop_db():
    """Drop all db tables."""
    drop_db_function()
    click.echo('Database dropped.')


def drop_db_function():
    db.drop_all()
    DB_COMMAND_LOGGER.info('Dropped Database.')


@click.command('init_db')
@with_appcontext
def init_db():
    """Fill the db with values."""
    init_db_function()
    click.echo('Database populated.')


def init_db_function():
    admin = User('admin', 'admin')
    admin_role = UserRole(admin, RoleEnum.admin)
    db.session.add(admin)
    db.session.add(admin_role)

    #add person unknown
    unknown = Person('Unbekannt', 'other')
    db.session.add(unknown)

    temp = History(MethodEnum.create, unknown, admin)
    db.session.add(temp)
    db.session.commit()
    DB_COMMAND_LOGGER.info('Database populated.')


@click.command('create_populated_db')
@with_appcontext
def create_populated_db():
    create_db_function()
    click.echo('Database created.')
    init_db_function()
    click.echo('Database populated.')
