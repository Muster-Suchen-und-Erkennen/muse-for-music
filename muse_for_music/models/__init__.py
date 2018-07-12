import click
from flask import Flask
from logging import Logger, StreamHandler, Formatter, getLogger, DEBUG
from sys import stdout
from sqlalchemy.engine import Engine
from sqlalchemy import event


from .. import app, db
from .users import User, UserRole, RoleEnum

DB_COMMAND_LOGGER = getLogger(app.logger_name + '.db')  # type: Logger

formatter = Formatter(fmt='[%(levelname)s] [%(name)-16s] %(message)s')

handler = StreamHandler(stream=stdout)

handler.setFormatter(formatter)

DB_COMMAND_LOGGER.addHandler(handler)

DB_COMMAND_LOGGER.setLevel(DEBUG)

from . import taxonomies
from . import data
from .data.people import Person
from .data.history import History, MethodEnum


if app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('sqlite://'):
    @event.listens_for(Engine, 'connect')
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if app.config.get('SQLITE_FOREIGN_KEYS', True):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()


@app.cli.command('create_db')
def create_db():
    """Create all db tables."""
    create_db_function()
    click.echo('Database created.')


def create_db_function():
    db.create_all()
    DB_COMMAND_LOGGER.info('Database created.')


@app.cli.command('drop_db')
def drop_db():
    """Drop all db tables."""
    drop_db_function()
    click.echo('Database dropped.')


def drop_db_function():
    db.drop_all()
    DB_COMMAND_LOGGER.info('Dropped Database.')


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

    temp = History(MethodEnum.create, unknown, admin)
    db.session.add(temp)
    db.session.commit()
    DB_COMMAND_LOGGER.info('Database populated.')


@app.cli.command('create_populated_db')
def create_populated_db():
    create_db_function()
    click.echo('Database created.')
    init_db_function()
    click.echo('Database populated.')
