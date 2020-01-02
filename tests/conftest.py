from os import environ
from pathlib import Path
import tempfile
from flask import Flask
import pytest

from util import AuthActions

from muse_for_music import create_app, db
from muse_for_music.models import create_db_function, init_db_function
from muse_for_music.models.taxonomies import get_taxonomies, generate_na_elements, DB_COMMAND_LOGGER
from muse_for_music.models.taxonomies.helper_classes import TreeTaxonomy, ListTaxonomy


@pytest.fixture
def tempdir():
    tempdir = tempfile.mkdtemp(prefix='muse-for-music-test-')
    yield tempdir
    tdir = Path(tempdir)
    for f in tdir.glob('**/*'):
        if f.is_dir():
            f.rmdir()
        else:
            f.unlink()
    tdir.rmdir()


@pytest.fixture
def app(tempdir):
    environ['MODE'] = 'test'
    environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/test.db'.format(tempdir)
    app = create_app()
    with app.app_context():
        # create db tables and initial values
        create_db_function()
        init_db_function()
    yield app


@pytest.fixture
def client(app: Flask):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def auth(client):
    return AuthActions(client)


@pytest.fixture
def taxonomies(app):
    with app.app_context():
        taxonomies = get_taxonomies()
        for name, tax in taxonomies.items():
            if issubclass(tax, TreeTaxonomy):
                root = tax(name='root', description=None)
                db.session.add(root)
                a = tax(name='{name}-{number}'.format(name=name, number=1), parent=root, description=None)
                b = tax(name='{name}-{number}'.format(name=name, number=2), parent=root, description=None)
                db.session.add(a)
                db.session.add(b)
                for i in range(3):
                    db.session.add(tax(name='{name}-{number}'.format(name=name, number=i+3), parent=a, description=None))
                    db.session.add(tax(name='{name}-{number}'.format(name=name, number=i+6), parent=b, description=None))
            elif issubclass(tax, ListTaxonomy):
                for i in range(5):
                    db.session.add(tax(name='{name}-{number}'.format(name=name, number=i), description=None))
        db.session.commit()
        generate_na_elements()
        yield taxonomies
        for tax in taxonomies.values():
            tax.clear_all(DB_COMMAND_LOGGER)
