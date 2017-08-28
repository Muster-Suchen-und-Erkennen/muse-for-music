import click
from flask import Flask, logging
from logging import Logger, StreamHandler, Formatter
from sys import stdout


from .. import app, db
from .users import User, UserRole, RoleEnum

DB_COMMAND_LOGGER = logging.create_logger(app)  # type: Logger

formatter = Formatter(fmt='[%(levelname)s] [%(name)-16s] %(message)s')

handler = StreamHandler(stream=stdout)

handler.setFormatter(formatter)

DB_COMMAND_LOGGER.addHandler(handler)

from . import taxonomies
from . import data
from .data.people import Person


@app.cli.command('create_db')
def create_db():
    """Create all db tables."""
    create_db_function()
    click.echo('Database created.')


def create_db_function():
    db.create_all()
    app.logger.info('Database created.')


@app.cli.command('drop_db')
def drop_db():
    """Drop all db tables."""
    drop_db_function()
    click.echo('Database dropped.')


def drop_db_function():
    db.drop_all()
    app.logger.info('Dropped Database.')


@app.cli.command('init_db')
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
    db.session.commit()
    app.logger.info('Database populated.')


@app.cli.command('create_populated_db')
def create_populated_db():
    create_db_function()
    click.echo('Database created.')
    init_db_function()
    click.echo('Database populated.')
