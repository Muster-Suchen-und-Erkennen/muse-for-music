from logging import Logger, StreamHandler, Formatter, getLogger, DEBUG
from sys import stdout
from flask import Flask, Blueprint
from flask.cli import with_appcontext
import click


from .. import db
from .users import User, UserRole, RoleEnum

DB_CLI = Blueprint('db_cli', __name__, cli_group=None)

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


@DB_CLI.cli.command('create_db')
@with_appcontext
def create_db():
    """Create all db tables."""
    create_db_function()
    click.echo('Database created.')


def create_db_function():
    db.create_all()
    DB_COMMAND_LOGGER.info('Database created.')


@DB_CLI.cli.command('drop_db')
@with_appcontext
def drop_db():
    """Drop all db tables."""
    drop_db_function()
    click.echo('Database dropped.')


def drop_db_function():
    db.drop_all()
    DB_COMMAND_LOGGER.info('Dropped Database.')


@DB_CLI.cli.command('init_db')
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


@DB_CLI.cli.command('create_populated_db')
@with_appcontext
def create_populated_db():
    create_db_function()
    click.echo('Database created.')
    init_db_function()
    click.echo('Database populated.')


def list_users_function():
    return [u.username for u in User.query.all()]


@DB_CLI.cli.command('list-users')
@with_appcontext
def list_users():
    users = list_users_function()
    click.echo('Registered users: ' + ', '.join(users))


def reset_password_function(username, password):
    user = User.query.filter(User.username == username).first()
    if user is None:
        DB_COMMAND_LOGGER.info('User %s was not found.', username)
        return
    user.set_password(password)
    DB_COMMAND_LOGGER.info('Setting new Password for user %s!', username)
    db.session.add(user)
    db.session.commit()


@DB_CLI.cli.command('set-user-password')
@click.option("--username", required=True)
@click.password_option("--password")
@with_appcontext
def reset_password(username, password):
    click.echo('Resetting password for user ' + username)
    reset_password_function(username, password)
